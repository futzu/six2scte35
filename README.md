# `six2scte35`
##### _six2scte35 requires threefive version >= 2.3.65_ 

### ffmpeg changes SCTE-35 stream type from 0x86 to 0x6
### six2scte35 changes it back.

### `before`
```lua
a@debian:~/bfm/mo$ ffprobe -hide_banner tested2.ts
Input #0, mpegts, from 'tested2.ts':
  Duration: 00:00:38.92, start: 1.400000, bitrate: 8453 kb/s
 
  Stream #0:0[0x100]: Data: bin_data ([6][0][0][0] / 0x0006)         <-- Boo, hiss.
  
  Stream #0:1[0x101]: Video: mpeg2video (Main) ([2][0][0][0] / 0x0002), 
  yuv420p(tv, bt470bg, top first), 1280x720 [SAR 1:1 DAR 16:9], 8000 kb/s, 50 fps, 50 tbr, 90k tbn
  Stream #0:2[0x102]: Audio: mp1 ([6][0][0][0] / 0x0006), 48000 Hz, stereo, s16p, 256 kb/s

```
### `six2scte35`
```lua
a@debian:~/bfm/mo$ ./six2scte35.py -i tested2.ts -p 256 -o tested3.ts
```
### `after`
```lua
a@debian:~/bfm/mo$ ffprobe -hide_banner tested3.ts
Input #0, mpegts, from 'tested3.ts':
  Duration: 00:00:38.92, start: 1.400000, bitrate: 8453 kb/s
 
  Stream #0:0[0x100]: Data: scte_35               <--      Boom << Boom.
  
  Stream #0:1[0x101]: Video: mpeg2video (Main) ([2][0][0][0] / 0x0002), 
  yuv420p(tv, bt470bg, top first), 1280x720 [SAR 1:1 DAR 16:9], 8000 kb/s, 50 fps, 50 tbr, 90k tbn
  Stream #0:2[0x102]: Audio: mp1 ([6][0][0][0] / 0x0006), 48000 Hz, stereo, s16p, 256 kb/s

```
### Version 0.0.3 adds pipe support

```js
a@debian:~$ pypy3 six2scte35.py -v
0.0.3
a@debian:~$ 

```

* Here's the input
```js
a@debian:~$ ffprobe pv.ts -hide_banner
[mpegts @ 0x55ddbc4045c0] start time for stream 5 is not set in estimate_timings_from_pts
Input #0, mpegts, from 'pv.ts':
  Duration: 00:00:20.33, start: 1.400000, bitrate: 17696 kb/s
  Program 1 
    Metadata:
      service_name    : Service01
      service_provider: FFmpeg
  Stream #0:0[0x100]: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p(tv, bt709, progressive), 1280x720 [SAR 1:1 DAR 16:9], Closed Captions, 59.94 fps, 59.94 tbr, 90k tbn
  Stream #0:1[0x101]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:2[0x102]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:3[0x103]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:4[0x104]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:5[0x105]: Data: bin_data ([6][0][0][0] / 0x0006)
Unsupported codec with id 98314 for input stream 5
a@debian:~$ 
```
* then I ran this command 
```js
a@debian:~$ cat pv.ts | pypy3 six2scte35.py -p 0x105 | ffplay -hide_banner  -
```

* output 
```js
261
pid match
Input #0, mpegts, from 'pipe:':    0KB vq=    0KB sq=    0B f=0/0   
  Duration: N/A, start: 1.400000, bitrate: N/A
  Program 1 
    Metadata:
      service_name    : Service01
      service_provider: FFmpeg
  Stream #0:0[0x100]: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p(tv, bt709, progressive), 1280x720 [SAR 1:1 DAR 16:9], Closed Captions, 59.94 fps, 59.94 tbr, 90k tbn
  Stream #0:1[0x101]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:2[0x102]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:3[0x103]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:4[0x104]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:5[0x105]: Data: scte_35
  17.30 A-V: -0.019 fd=   0 aq=   32KB vq= 2498KB sq=    0B f=0/0   
```

*  to write to a file 
```js
a@debian:~$ cat pv.ts | pypy3 six2scte352.py -p 0x105 -o kout.ts
261
pid match
```
```js
ffprobe -hide_banner kout.ts
Input #0, mpegts, from 'kout.ts':
  Duration: 00:00:20.24, start: 1.400000, bitrate: 17650 kb/s
  Program 1 
    Metadata:
      service_name    : Service01
      service_provider: FFmpeg
  Stream #0:0[0x100]: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p(tv, bt709, progressive), 1280x720 [SAR 1:1 DAR 16:9], Closed Captions, 59.94 fps, 59.94 tbr, 90k tbn
  Stream #0:1[0x101]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:2[0x102]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:3[0x103]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:4[0x104]: Audio: mp2 ([3][0][0][0] / 0x0003), 48000 Hz, stereo, fltp, 256 kb/s
  Stream #0:5[0x105]: Data: scte_35
Unsupported codec with id 98305 for input stream 5
```

* so you can do something like 
```js
 ffmpeg -i  mpegts/pcrvid.ts -map 0 -c copy -f mpegts - | pypy3 six2scte35.py -p 0x105 | ffplay  -

```




