#!/usr/bin/env pypy3

import argparse
import io
import sys
from functools import partial
from new_reader import reader
from threefive import Stream
from threefive.crc import crc32
from bitn import NBin


class Stream2(Stream):
    CUEI_DESCRIPTOR = b"\x05\x04CUEI"

    def __init__(self, tsdata=None):

        self.pmt_payload = None
        self.con_pid = None
        self.out_file = None
        self.in_file = None
        self._parse_args()
        print(self.in_file)
        super().__init__(self.in_file)

    def _parse_args(self):
        """
        _parse_args parse command line args
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i",
            "--input",
            default=None,
            help=""" Input source, like "/home/a/vid.ts"
                                    or "udp://@235.35.3.5:3535"
                                    or "https://futzu.com/xaa.ts"
                                    """,
        )

        parser.add_argument(
            "-o",
            "--output",
            default="0x6to0x86.ts",
            help="""Output file """,
        )

        parser.add_argument(
            "-p",
            "--convert_pid",
            default=None,
            help="""Pid to change to type 0x86 (SCTE-35)  """,
        )
        parser.add_argument(
            "-v",
            "--version",
            action="store_const",
            default=False,
            const=True,
            help="Show version",
        )

        args = parser.parse_args()
        self._apply_args(args)

    def _apply_args(self, args):
        if args.convert_pid and args.input:
            self.out_file = args.output
            self.in_file = args.input
            self._tsdata = reader(args.input)
            self.con_pid2int(args.convert_pid)
        else:
            print(" input file and pid to convert are required. run kabuki -h")
            sys.exit()

    def iter_pkts(self):
        return iter(partial(self._tsdata.read, self._PACKET_SIZE), b"")

    def con_pid2int(self, pid):
        if pid.startswith("0x"):
            self.con_pid = int(pid, 16)
        else:
            self.con_pid = int(pid)
        print(self.con_pid)

    def convert_pid(self):
        """
        Stream.decode_proxy writes all ts packets are written to stdout
        for piping into another program like mplayer.
        SCTE-35 cues are printed to stderr.
        """
        if self._find_start():
            active = io.BytesIO()
            pkt_count = 0
            chunk_size = 2048
            #  print("hi")
            with reader(self.in_file) as fu, open(self.out_file, "wb") as out_file:
                for pkt in iter(partial(fu.read, self._PACKET_SIZE), b""):
                    # print(pkt)
                    pid = self._parse_pid(pkt[1], pkt[2])
                    if pid in self.pids.tables:
                        self._parse_tables(pkt, pid)
                    if pid in self.pids.pmt:
                        if self.pmt_payload:
                            pkt = pkt[:4] + self.pmt_payload
                            # print('PMT')
                    active.write(pkt)
                    pkt_count = (pkt_count + 1) % chunk_size
                    if not pkt_count:
                        out_file.write(active.getbuffer())
                        active = io.BytesIO()
                out_file.write(active.getbuffer())

    def _regen_pmt(self, n_seclen, pcr_pid, n_proginfolen, n_info_bites, n_streams):
        nbin = NBin()
        nbin.add_int(2, 8)  # 0x02
        nbin.add_int(1, 1)  # section Syntax indicator
        nbin.add_int(0, 1)  # 0
        nbin.add_int(3, 2)  # reserved
        nbin.add_int(n_seclen, 12)  # section length
        nbin.add_int(1, 16)  # program number
        nbin.add_int(3, 2)  # reserved
        nbin.add_int(0, 5)  # version
        nbin.add_int(1, 1)  # current_next_indicator
        nbin.add_int(0, 8)  # section number
        nbin.add_int(0, 8)  # last section number
        nbin.add_int(7, 3)  # res
        nbin.add_int(pcr_pid, 13)
        nbin.add_int(15, 4)  # res
        nbin.add_int(n_proginfolen, 12)
        nbin.add_bites(n_info_bites)
        nbin.add_bites(n_streams)
        a_crc = crc32(nbin.bites)
        nbin.add_int(a_crc, 32)
        n_payload = nbin.bites
        pad = 187 - (len(n_payload) + 4)
        pointer_field = b"\x00"
        if pad > 0:
            n_payload = pointer_field + n_payload + (b"\xff" * pad)
        self.pmt_payload = n_payload

    def _program_map_table(self, pay, pid):
        """
        parse program maps for streams
        """
        pay = self._chk_partial(pay, pid, self._PMT_TID)
        if not pay:
            return False
        seclen = self._parse_length(pay[1], pay[2])
        n_seclen = seclen + 6
        if not self._section_done(pay, pid, seclen):
            return False
        program_number = self._parse_program(pay[3], pay[4])
        pcr_pid = self._parse_pid(pay[8], pay[9])
        self.pids.pcr.add(pcr_pid)
        self.maps.pid_prgm[pcr_pid] = program_number
        proginfolen = self._parse_length(pay[10], pay[11])
        idx = 12
        n_proginfolen = proginfolen + len(self.CUEI_DESCRIPTOR)
        end = idx + proginfolen
        info_bites = pay[idx:end]
        n_info_bites = info_bites + self.CUEI_DESCRIPTOR
        while idx < end:
            # d_type = pay[idx]
            idx += 1
            d_len = pay[idx]
            idx += 1
            # d_bytes = pay[idx - 2 : idx + d_len]
            idx += d_len
        si_len = seclen - 9
        si_len -= proginfolen
        n_streams = self._parse_program_streams(si_len, pay, idx, program_number)
        self._regen_pmt(n_seclen, pcr_pid, n_proginfolen, n_info_bites, n_streams)
        return True

    def _parse_program_streams(self, si_len, pay, idx, program_number):
        """
        parse the elementary streams
        from a program
        """
        chunk_size = 5
        end_idx = (idx + si_len) - 4
        start = idx
        while idx < end_idx:
            pay, stream_type, pid, ei_len = self._parse_stream_type(pay, idx)
            idx += chunk_size
            idx += ei_len
            self.maps.pid_prgm[pid] = program_number
            self._chk_pid_stream_type(pid, stream_type)
        # crc = pay[idx : idx + 4]
        streams = pay[start:end_idx]
        return streams

    def _parse_stream_type(self, pay, idx):
        """
        extract stream pid and type
        """
        npay = pay
        stream_type = pay[idx]
        el_pid = self._parse_pid(pay[idx + 1], pay[idx + 2])
        #  print(self.con_pid,el_pid)
        if el_pid == self.con_pid:
            print("pid match")
            if stream_type == 6:
                npay = pay[:idx] + b"\x86" + pay[idx + 1 :]
        ei_len = self._parse_length(pay[idx + 3], pay[idx + 4])
        return npay, stream_type, el_pid, ei_len


if __name__ == "__main__":

    s = Stream2()
    s.convert_pid()
