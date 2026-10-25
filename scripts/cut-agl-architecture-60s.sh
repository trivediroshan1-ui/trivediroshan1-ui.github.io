#!/bin/sh
# 60-second WhatsApp cut of the architecture video: master, gateway, bypass layer 1, then the recap and link slide.
cd "$(dirname "$0")/.." || exit 1
IN=assets/share/agl-architecture.mp4
ffmpeg -v error -y -i "$IN" \
  -filter_complex "[0:v]trim=0:47,setpts=PTS-STARTPTS[a];[0:v]trim=111:122.5,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -c:v libx264 -crf 22 -pix_fmt yuv420p -movflags +faststart assets/share/agl-architecture-60s.mp4
ffmpeg -v error -y -ss 115 -i "$IN" -frames:v 1 assets/share/agl-master-architecture.png
ls -la assets/share/agl-architecture-60s.mp4 assets/share/agl-master-architecture.png
