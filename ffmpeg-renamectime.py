import sys, os, glob, getopt, subprocess, pathlib, json
from datetime import datetime, timezone
from subprocess import call
from os.path import exists
import re

# STATIC **********************************************************************

FILTER_EXTS = ['mp4', 'jpg', 'png']
OUTPUT_DATE_REG = r'^[0-9]{8}_[0-9]{6}.*'
OUTPUT_DATE_PATTERN = "%Y%m%d_%H%M%S"
METADATA_DATE_PATTERN = "%Y-%m-%dT%H:%M:%S.%f%z"

# PUBLIC **********************************************************************

class Item:
    index = 0
    input = ""
    datestr = ""
    
# PRIVATE *********************************************************************

def process(videosdirpath):
    print("Start")
    items = []
    items = getfiles(videosdirpath)
    items = filterbyext(items, FILTER_EXTS)
    for item in items:
        if hasdatename(item, OUTPUT_DATE_REG): 
            continue
        getctime(item, OUTPUT_DATE_PATTERN, METADATA_DATE_PATTERN)
        rename(item)

# FUNCTIONS *********************************************************************

def rename(item):
    dirname = os.path.dirname(item.input)
    basename = os.path.basename(item.input)
    item.oldname = item.input
    item.newname = f"{dirname}\{item.datestr}-{basename}"
    os.rename(item.oldname, item.newname)

def getctime(item, tpl, tpl2):
    ts = os.path.getctime(item.input)
    utc_dt = datetime.fromtimestamp(ts)
    if item.ext == 'mp4':
        utc_dt = getctimevideo(item, tpl2)
    loc_dt = utc_to_local(utc_dt) 
    ctime = utc_dt.astimezone().strftime(tpl)
    item.datestr = ctime

def getctimevideo(item, tpl2):
    metadata = FFProbe(item.input)
    for stream in metadata["streams"]:
        datestr = stream['tags']['creation_time']
        return datetime.strptime(datestr, tpl2)      

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
        item.ext = ext
        filtered.append(item)
    return filtered

# https://github.com/gbstack/ffprobe-python
def FFProbe(path):
    cmd = f"ffprobe.exe -show_format -show_streams -loglevel quiet -print_format json \"{path}\""
    json_data = subprocess.check_output(cmd, shell=True)
    json_object = json.loads(json_data)
    return json_object

# https://github.com/gbstack/ffprobe-python
def is_video(json):
    return json['codec_type'] == 'video'

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

# LOGS *********************************************************************

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
    print("FFMEPG Re-name with Create Time")
    print(f'Exec. path : {os.getcwd()}')
    # TODO: install()
    process(dirpath)

if __name__ == "__main__":
    main(sys.argv[1:])
