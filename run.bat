
SET DIRPATH="C:\Users\damien\Desktop\100MEDIA"

python .\ffmpeg-renamectime.py --dirpath %DIRPATH%
python .\ffmpeg-reencodex265.py --dirpath %DIRPATH%
@REM python .\ffmpeg-clean.py --dirpath %DIRPATH%