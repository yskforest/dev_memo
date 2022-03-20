# ffmpeg

## 30->60フレーム補完
```
ffmpeg -i input.mp4  -vf minterpolate=60:2:0:1:8:16:32:0:1:5 output.mp4
```

## 