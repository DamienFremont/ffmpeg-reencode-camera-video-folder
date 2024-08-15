# FFmpeg - Reencode Camera Video Folder (H265, Timestamp, Thumbnail)

![alt text](./docs/readme-thumb.png)

Useful for GoPro or DJI Drone videos. 

Reencode videos folder's content to x265, with thumbnails
(tested with ffmpeg "Latest Auto-Build (2022-09-13 12:39)")

Example : 
- Input `DJI_0721.MP4`
- Output `20221017_170300-DJI_0721-x265.mp4` (with thumbnail)

---

## Getting Started

Install Python 3, pip, ffmepg, mp4box.exe

```bash
pip install -r requirements.txt --force-reinstall

wget https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z
# unzip

wget https://gpac.wp.imt.fr/downloads/

```

![alt text](./docs/readme-install-1.png)

---

## Usage

```bash
python .\ffmpeg-renamectime.py --dirpath "C:\Users\damien\Desktop\100MEDIA"

python .\ffmpeg-reencodex265.py --dirpath "C:\Users\damien\Desktop\100MEDIA"
```

![alt text](./docs/readme-usage-1.png)

![alt text](./docs/readme-usage-2.png)

![alt text](./docs/readme-usage-3.png)

---

## Resources

- https://ffmpeg.org/
  - https://ffmpeg.org/download.html#build-windows
