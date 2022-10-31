import sys, os, glob, getopt, subprocess, pathlib, json
from datetime import datetime, timezone
from subprocess import call
from os.path import exists
import re

# STATIC **********************************************************************

FILTER_EXTS = ['mp4']
FILTER_CODECS = ['h264']
OUTPUT_SUFFIX = '-x265.mp4'
THUMB_SUFFIX = '.jpg'
THUMB_TS = "00:00:01"
OUTPUT_DATE_REG = r'^[0-9]{8}_[0-9]{6}.*'
OUTPUT_DATE_PREFIX = "%Y%m%d_%H%M%S-"
METADATA_DATE_PTRN = "%Y-%m-%dT%H:%M:%S.%f%z"

# PUBLIC **********************************************************************

class Item:
    index = 0
    input = ""
    output = ""
    thumb = ""
    video = ""
    audio = ""
    
# PRIVATE *********************************************************************

def process(videosdirpath):
    print("Start")
    items = []
    logconfig(videosdirpath)

    print("Step 1 : Find")
    items = getfiles(videosdirpath)
    items = filterbyext(items, FILTER_EXTS)
    items = filterbycodec(items, FILTER_CODECS)

    print("Step 2 : Prepare")
    for item in items:
        logsource(item)
        item.output = item.input
        setoutputcodec(item, OUTPUT_SUFFIX)
        if not hasdatename(item, OUTPUT_DATE_REG): 
            setoutputctime(item, OUTPUT_DATE_PREFIX, METADATA_DATE_PTRN)

    print("Step 3 : Encode")
    for item in items:
        logtarget(item)
        # if exists(item.output) :
        #     continue
        # TODO: temp folder
        createtemp(item)
        savevideo(item)
        saveaudio(item)
        savethumb(item, THUMB_TS)

    print("Step 4 : Mux")
    for item in items:
        # if exists(item.output) :
        #     continue
        logvideo(item)
        reencode(item)

    print('End')
    logcsv(items)

# FUNCTIONS *********************************************************************

def hasdatename(item, pattern):
    basename = os.path.basename(item.input)
    return re.match(pattern, basename)

def getfiles(path):
    items = []
    files = glob.glob(f"{path}/*.*")
    index = 0
    for file in files:
        item = Item()
        item.index = index
        item.input = file
        items.append(item)
        index = index + 1
    return items

def filterbyext(items, exts):
    filtered = []
    for item in items:
        ext = pathlib.Path(item.input).suffix
        ext = ext.replace('.','')
        ext = ext.lower()
        if not ext in exts:
            continue
        filtered.append(item)
    return filtered

# https://github.com/gbstack/ffprobe-python
def filterbycodec(items, codecs):
    filtered = []
    for item in items:
        metadata = FFProbe(item.input)
        for stream in metadata["streams"]:
            if not is_video(stream):
                continue
            if not codec(stream).lower() in codecs:
                continue    
            filtered.append(item)
    return filtered

# https://github.com/gbstack/ffprobe-python
def FFProbe(path):
    cmd = f"ffprobe.exe -show_format -show_streams -loglevel quiet -print_format json {path}"
    json_data = subprocess.check_output(cmd, shell=True)
    json_object = json.loads(json_data)
    return json_object

# https://github.com/gbstack/ffprobe-python
def is_video(json):
    return json['codec_type'] == 'video'
def is_audio(json):
    return json['codec_type'] == 'audio'
# https://github.com/gbstack/ffprobe-python
def codec(json):
    return json['codec_name']

def setoutputcodec(item, suffix):
    item.output = replacesuffix(item.output, suffix)

# TODO: add timezone param to CLI
def setoutputctime(item, tpl, tpl2):
    metadata = FFProbe(item.input)
    for stream in metadata["streams"]:
        if is_video(stream):
            datestr = stream['tags']['creation_time']
    utc_dt = datetime.strptime(datestr, tpl2)
    loc_dt = utc_to_local(utc_dt) 
    ctime = utc_dt.astimezone().strftime(tpl)
    filepath = item.output
    dirname = os.path.dirname(filepath)
    basename = os.path.basename(filepath)
    item.output = f"{dirname}\{ctime}{basename}"

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def replacesuffix(path, suffix):
    ext = pathlib.Path(path).suffix
    new = path.replace(ext, f"{suffix}")
    return new

def createtemp(item):
    folderpath = f"{item.output}_temp"
    item.temp = folderpath
    if exists(folderpath) :
        return
    os.mkdir(folderpath)
    print(f"Directory {folderpath} created")

def savethumb(item, ts):
    input = item.input
    filepath = os.path.join(item.temp, "thumb.jpg")
    overwrite = '-y'
    verbose = '-hide_banner -loglevel error'
    cmd = f"ffmpeg.exe -ss {ts} {overwrite} {verbose} -i \"{input}\" -frames:v 1 -q:v 2 \"{filepath}\""
    out = subprocess.check_output(cmd, shell=True)
    item.thumb = filepath

def savevideo(item):
    metadata = FFProbe(item.input)
    for stream in metadata["streams"]:
        if is_video(stream):
            filepath = os.path.join(item.temp, "video.h265")
            overwrite = '-y'
            verbose = '-hide_banner -loglevel error'
            cmd = f"ffmpeg.exe {overwrite} {verbose} -i \"{item.input}\" -c:v libx265 \"{filepath}\""
            out = subprocess.check_output(cmd, shell=True)
            item.video = filepath

def saveaudio(item):
    metadata = FFProbe(item.input)
    for stream in metadata["streams"]:
        if is_audio(stream):
            filepath = os.path.join(item.temp, "audio.m4a")
            cmd = f"MP4Box.exe -single 2 -out \"{filepath}\" \"{item.input}\""
            out = subprocess.check_output(cmd, shell=True)
            item.audio = filepath

def reencode(item):
    cmdvideo = f" -add \"{item.video}#video:name=\" " if hasattr(item, 'video') else ""
    cmdaudio = f" -add \"{item.audio}#audio:name=\" " if hasattr(item, 'audio') else ""
    cmdthumb = f" -itags cover=\"{item.thumb}\" " if hasattr(item, 'thumb') else ""
    overwrite = '-y'
    verbose = '-hide_banner -loglevel error'
    cmd = f"MP4Box.exe {cmdvideo} {cmdaudio} {cmdthumb} -new \"{item.output}\""
    out = subprocess.check_output(cmd, shell=True)

# LOGS *********************************************************************

def logconfig(path):
    print("")
    print("---------------------------- Configuration ----------------------------")
    print("")
    print(f"Input")
    print(f"folder: {path}")
    print(f"filter (exts): {FILTER_EXTS}")
    print(f"filter (codecs): {FILTER_CODECS}")
    print("")
    print(f"Output")
    print(f"name: *{OUTPUT_SUFFIX}")
    print("")

def logsource(item):
    print("")
    print("------------------------- Source Script Info -------------------------")
    print("")
    print(f"index: {item.index}")
    print(f"input: {item.input}")
    print("")

def logtarget(item):
    print("")
    print("------------------------- Target Script Info -------------------------")
    print("")
    print(f"output: {item.output}")
    print("")

def logvideo(item):
    print("")
    print("------------------------- Video encoding x265 -------------------------")
    print("")
    
def logvideo(item):
    print("")
    print("---------------------------- Muxing to MP4 ----------------------------")
    print("")

def logcsv(items):
    print("")
    print("-------------------------- Printing to CSV ----------------------------")
    print("")
    print(f"index;input;output;archive;")
    for item in items:
        print(f"{item.index};{item.input};{item.output};")
    print("")

# UTILS *********************************************************************

# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def getargs(argv, configs, helpmsg=None):
    """getargs(argv, configs, helpmsg)
    
    Return dictionnary with long opt names as keys and arg as values. 
    From Reading command line arguments, using short or long opt names with default values from configs object.

    Parameters
    ----------
    argv
        |sys.argv[1:]|
    configs
        |array<dictionnary['opt':str,'shortopt':str,'longopt':str,'defarg':str]>|
        example : [{'opt':'myopt'},...] or [{'shortopt':'mo','longopt':'myopt','defarg':'False'},...]
    helpmsg
        |str(optionnal)|
        example : 'python myscript.py -m <myopt>'

    Returns
    -------
    dictionnary[key(longopt):str(arg or defarg)]

    Usage
    -----
    argv = sys.argv[1:]

    helpmsg = 'python myscript.py -m <myopt>'

    configs = [{ 'opt':'myopt', 'defarg':'False' } ]

    argdic = getargs(argv, configs, helpmsg)

    myoptarg = argdic.get('myopt')
    """
    shortopts = "h"
    longopts = []
    defhelpmsg = 'Usage: python [script].py'
    for conf in configs:
        # DEF VALS
        if not 'longopt' in conf.keys():
            conf['longopt'] = conf['opt']
        if not 'shortopt' in conf.keys():
            conf['shortopt'] = conf['longopt'][0]
        if not 'defarg' in conf.keys():
            conf['defarg'] = None
        # BUILD PARAMS
        shortopts += f"{conf['shortopt']}:"
        longopts.append(f"{conf['longopt']}=")
        defhelpmsg += f" --{conf['longopt']} <{conf['defarg']}>"
    help = defhelpmsg if helpmsg is None else helpmsg
    # READ OPT
    try:
        opts, args = getopt.getopt(argv,shortopts,longopts)
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    # GET ARGS
    res = {}
    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit()
        else:
            for conf in configs:
                if opt in (f"-{conf['shortopt']}", f"--{conf['longopt']}"):
                    res[conf['longopt']] = arg
                    continue
    # DEFAULT ARGS
    print("Running default command line with: ")
    for conf in configs:
        if not conf['longopt'] in res.keys():
            res[conf['longopt']] = conf['defarg']
        print(f"argument --{conf['longopt']}: '{res[conf['longopt']]}'")
    return res

# SCRIPT **********************************************************************

def main(argv):
    argd = getargs(argv, [
        { 'opt':'dirpath',  'defarg':'.' }])
    dirpath = argd.get("dirpath")
    print("FFMEPG Re-encode")
    print(f'Exec. path : {os.getcwd()}')
    # TODO: install()
    process(dirpath)

if __name__ == "__main__":
    main(sys.argv[1:])
