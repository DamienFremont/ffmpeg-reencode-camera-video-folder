import sys, os, glob, getopt, subprocess, pathlib, json
from datetime import datetime, timezone
from subprocess import call
from os.path import exists
import shutil

# STATIC **********************************************************************

FILTER = '_temp'

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
    items = getfiles(videosdirpath, FILTER)

    print("Step 2 : Prepare")
    for item in items:
        deltempfolder(item, FILTER)
        delinputfile(item)

# FUNCTIONS *********************************************************************

def deltempfolder(item, ext):
    myfile = f"{item.input}{ext}"
    if os.path.isdir(myfile):
        print(f"del {myfile}")
        shutil.rmtree(myfile, ignore_errors=False, onerror=None)  

def delinputfile(item):
    myfile = item.input
    if os.path.isfile(myfile):
        print(f"del {myfile}")
        os.remove(myfile)

def getfiles(path, filter):
    items = []
    files = glob.glob(f"{path}/*{filter}")
    index = 0
    for file in files:
        item = Item()
        item.index = index
        item.input = file.replace(filter, '')
        items.append(item)
        index = index + 1
    return items

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
    print("FFMEPG clean temp and old files")
    print(f'Exec. path : {os.getcwd()}')
    # TODO: install()
    process(dirpath)

if __name__ == "__main__":
    main(sys.argv[1:])
