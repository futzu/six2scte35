# kabuki
ffmpeg changes SCTE-35 stream type from 0x86 to 0x6, kabuki changes it back to SCTE-35

```smalltalk
a@debian:~/bfm/mo$ pypy3 kabuki.py -h
usage: kabuki.py [-h] [-i INPUT] [-o OUTPUT] [-p CONVERT_PID] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input source, like "/home/a/vid.ts" or "udp://@235.35.3.5:3535" or
                        "https://futzu.com/xaa.ts"
  -o OUTPUT, --output OUTPUT
                        Output file
  -p CONVERT_PID, --convert_pid CONVERT_PID
                        Pid to change to type 0x86 (SCTE-35)
  -v, --version         Show version
```
