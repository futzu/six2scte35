# `kabuki`
ffmpeg changes SCTE-35 stream type from 0x86 to 0x6, kabuki changes it back to SCTE-35

### `before`
```lua
a@debian:~/bfm/mo$ ffprobe -hide_banner tested2.ts
[mpegts @ 0x56027349d580] start time for stream 0 is not set in estimate_timings_from_pts
Input #0, mpegts, from 'tested2.ts':
  Duration: 00:00:38.92, start: 1.400000, bitrate: 8453 kb/s
  Program 1 
    Metadata:
      service_name    : Service01
      service_provider: FFmpeg
      
      
      
  Stream #0:0[0x100]: Data: bin_data ([6][0][0][0] / 0x0006)         <-- Boo, hiss.
  
  
  
  Stream #0:1[0x101]: Video: mpeg2video (Main) ([2][0][0][0] / 0x0002), yuv420p(tv, bt470bg, top first), 1280x720 [SAR 1:1 DAR 16:9], 8000 kb/s, 50 fps, 50 tbr, 90k tbn
    Side data:
      cpb: bitrate max/min/avg: 8000000/0/0 buffer size: 3178496 vbv_delay: N/A
  Stream #0:2[0x102]: Audio: mp1 ([6][0][0][0] / 0x0006), 48000 Hz, stereo, s16p, 256 kb/s
  Stream #0:3[0x103]: Data: bin_data ([6][0][0][0] / 0x0006)
Unsupported codec with id 98314 for input stream 0
Unsupported codec with id 98314 for input stream 3
```
### `kabuki`
```lua
a@debian:~/bfm/mo$ ./kabuki.py -i tested2.ts -p 256 -o tested3.ts
```
### `after`
```lua
a@debian:~/bfm/mo$ ffprobe -hide_banner tested3.ts
[mpegts @ 0x55d1f4c65580] start time for stream 0 is not set in estimate_timings_from_pts
Input #0, mpegts, from 'tested3.ts':
  Duration: 00:00:38.92, start: 1.400000, bitrate: 8453 kb/s
  Program 1 
    Metadata:
      service_name    : Service01
      service_provider: FFmpeg
  
  
      
  Stream #0:0[0x100]: Data: scte_35                                 <--      Boom << Boom.
  
  
  
  Stream #0:1[0x101]: Video: mpeg2video (Main) ([2][0][0][0] / 0x0002), yuv420p(tv, bt470bg, top first), 1280x720 [SAR 1:1 DAR 16:9], 8000 kb/s, 50 fps, 50 tbr, 90k tbn
    Side data:
      cpb: bitrate max/min/avg: 8000000/0/0 buffer size: 3178496 vbv_delay: N/A
  Stream #0:2[0x102]: Audio: mp1 ([6][0][0][0] / 0x0006), 48000 Hz, stereo, s16p, 256 kb/s
  Stream #0:3[0x103]: Data: bin_data ([6][0][0][0] / 0x0006)
Unsupported codec with id 98305 for input stream 0
Unsupported codec with id 98314 for input stream 3

```

