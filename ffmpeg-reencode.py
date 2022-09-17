import sys, os, glob, getopt, subprocess, pathlib, json
from subprocess import call
from os.path import exists

# STATIC **********************************************************************

FILTER_EXTS = ['mp4']
FILTER_CODECS = ['h264']
OUTPUT_SUFFIX = '-x265.mp4'
THUMB_SUFFIX = '-thumb.jpg'
THUMB_TS = "00:00:01"

# PUBLIC **********************************************************************

class Item:
    index = 0
    input = ""
    output = ""
    thumb = ""
    
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
        setthumb(item, THUMB_SUFFIX)
        if exists(item.thumb) :
            break
        savethumb(item)

    print("Step 3 : Encode")
    for item in items:
        setoutput(item, OUTPUT_SUFFIX)
        logtarget(item)
        if exists(item.output) :
            break
        logvideo(item)
        reencode(item)

    print('End')
    logcsv(items)

# FUNCTIONS *********************************************************************

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
            break
        filtered.append(item)
    return filtered

# https://github.com/gbstack/ffprobe-python
def filterbycodec(items, codecs):
    filtered = []
    for item in items:
        metadata = FFProbe(item.input)
        for stream in metadata["streams"]:
            if not is_video(stream):
                break
            if not codec(stream).lower() in codecs:
                break    
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
# https://github.com/gbstack/ffprobe-python
def codec(json):
    return json['codec_name']

def setoutput(item, suffix):
    item.output = item.input
    item.output = replacesuffix(item.output, suffix)

def replacesuffix(path, suffix):
    ext = pathlib.Path(path).suffix
    new = path.replace(ext, f"{suffix}")
    return new

def setthumb(item, suffix):
    item.thumb = replacesuffix(item.input, suffix)

def savethumb(item):
    input = item.input
    output = item.thumb
    ts = THUMB_TS
    cmd = f"ffmpeg.exe -ss {ts} -i \"{input}\" -frames:v 1 -q:v 2 \"{output}\""
    out = subprocess.check_output(cmd, shell=True)

def reencode(item):
    input = item.input
    output = item.output
    cmd = f"ffmpeg.exe -i \"{input}\" -c:v libx265 \"{output}\""
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
    print(f"thumb: {item.thumb}")
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
        print(f"{item.index};{item.input};{item.output};{item.archive};")
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
    process(dirpath)

if __name__ == "__main__":
    main(sys.argv[1:])
