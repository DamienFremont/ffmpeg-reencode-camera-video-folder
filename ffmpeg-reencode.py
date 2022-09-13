import sys, os, glob, getopt, time, pathlib

# STATIC **********************************************************************

DEFAULT_EXTS = ['mp4']
DEFAULT_CODECS = ['h264']
TMP_DIR = '_tmp'
# RES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), RES_DIR)

# PUBLIC **********************************************************************

class Item:
    index = 0
    path = ""
    desfile = ""
    thumb = ""
    
# PRIVATE *********************************************************************

def process(videosdirpath):
    items = []
    print("STEP 1 : FIND")
    items = listfiles(videosdirpath)
    items = filterbyext(items, DEFAULT_EXTS)
    # items = filterbycodec(items, DEFAULT_CODECS)   
    print("STEP 2 : PREPARE")
    # items = createthumbs(items)
    # items = namedateprefix(items)
    print("STEP 3 : ENCODE")
    # items = namecodecsuffix(items)
    # items = reencode(items)
    print("STEP 4 : ARCHIVE")
    # items = createarchivedir()
    # items = archive(items)
    print('Batch Result:')

def listfiles(path):
    items = []
    files = glob.glob(f"{path}/*.*")
    index = 0
    for file in files:
        item = Item()
        item.index = index
        item.path = file
        items.append(item)
        index = index + 1
    return items

def filterbyext(items, exts):
    print(f"finding files with exts={exts}...")
    filtered = []
    for item in items:
        ext = pathlib.Path(item.path).suffix
        ext = ext.replace('.','')
        ext = ext.lower()
        if ext in exts:
            filtered.append(item)
            print(f"{item.index}: {item.path}")
    return items

def getfileext(path):
    return 

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
