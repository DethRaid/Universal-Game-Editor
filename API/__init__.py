# -*- coding: utf8 -*-
"""TODO"""
# noinspection PyUnresolvedReferences
from . import addedbuiltins
from sys import modules, path

# IMPORTANT: DO NOT CHANGE!
__major__,__minor__,__revision__ = 3,0,6
version = '%s.%s.%s'%(__major__,__minor__,__revision__)

import imp
# Tcll - for API-security reasons, this verifies we are not importing the API from within API execution.
# direct access to ALL UGE-API internals is not allowed (including libraries)
def secure_importer(name, globals=None, locals=None, fromlist=None):
    
    # Fast path: see if the module has already been imported.
    if name in modules: return modules[name]

    # If any of the following calls raises an exception,
    # there's a problem we can't handle -- let the caller handle it.

    fp, pathname, description = imp.find_module(name)

    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

#__builtins__['__import__']=secure_importer # replace the import statement

import os, re
from . import plugin
from zipimport import zipimporter as zi
from ast import AST, PyCF_ONLY_AST, Str, Call

from . import CONST, OBJECT

CPU_ARCH = 'x86' # or 'x64'
CWD = __file__.split('API')[0].replace('\\','/') # Tcll - I don't trust the os module
# NOTE: all sub-paths should be regulated to use '/', like most OS's 

def getstream(name):
    # NOTE: originally designed for DLLs, then extended for EGGs, WHLs, and ZIPs
    import sys
    frame = sys._getframe()
    while frame and '__name__' in frame.f_globals:
        globName = frame.f_globals['__name__']
        if globName not in ['API'] and '.' not in globName: break
        frame = frame.f_back
    del frame
    
    plg = modules[globName]
    path = os.path.sep.join( ('%sbin'%plg.__dict__['__file__'].split('__init__')[0], CPU_ARCH, name) ) # load *plugin*/bin/x**/***.(dll/dylib/so.#)
    if '__loader__' in plg.__dict__: return plg.__dict__['__loader__'].get_data(path)
    else: # plugin is in development (unzipped)
        with open(path,'rb') as mod: return mod.read() # simulation of the zipped environment (note that open cannot load from a zipped file)

def tmpcpy(name):
    with open(os.path.sep.join( (CWD, 'tmp', name) ),'wb') as mod: mod.write(getstream(name)) # copy the module to the temporary search path

os.environ['PATH'] += ';'+CWD+os.path.sep+'tmp' # temporary DLL search path (to be removed)
def ugeLoadBinary(name,copy=True):
    """return a loaded binary module CDLL instance from it's data stream"""

    '''
    PAGE_REWRITE = 0x04
    PROCESS_ALL_ACCESS = 0x00F0000|0x00100000|0xFFF
    VIRTUAL_MEM = 0x1000|0x2000
    
    stream = getstream(name) # data-stream from binary module name
    # Tcll - don't have anything for mac or linux yet -_-
    if sys.platform=='win32':
        kernel32=ctypes.windll.kernel32
        # Get handle to process being injected
        handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS,False, int(PID) )
    # now why can't zipimport do this 9_9
    '''

    # TODO: (copying files is stupid) inject the module-stream into a new process and get it's handle.
    if copy: handle=None; tmpcpy(name)
    # NOTE: passing a handle to CDLL won't initialize _dlload('name') and CDLL will assume it's already loaded
    return ctypes.CDLL(name,handle=handle)

def ugeLoadExtension(name):
    """load a zipped python-extension (egg/whl) from it's data stream"""
    # TODO: (copying files is stupid) hack the zipimport class to load a data stream with a given name.
    tmpcpy(name)
    path.append('tmp/%s'%name)

loadedPlugins = []
# noinspection PyBroadException
def loadPlugins(pluginDir = 'plugins'):
    path.append(pluginDir)
    global loadedPlugins

    DevMode = True

    print( 'Loading Plugins:')
    ext = '.zip'
    for package in os.listdir(pluginDir):
        pkgpath='%s/%s'%(pluginDir.replace('\\','/'),package) # plugins/plugin.zip
    
        if os.path.isfile(pkgpath) and pkgpath.endswith(ext):
            if DevMode and os.path.exists('/'.join((pkgpath[:-len(ext)],'__init__.py'))): continue # skip if in-dev.
            _name=pkgpath.split('/')[-1][:-len(ext)]
            print( '|   %s'%_name)
            try: path.append(pkgpath); loadedPlugins.append( zi(pkgpath).load_module(_name) )
            except: # invalid plugin
                import sys, traceback
                print(); traceback.print_exception(*sys.exc_info()); print()

        if DevMode and os.path.exists('/'.join((pkgpath,'__init__.py'))):
            _name=pkgpath.split('/')[-1]
            print( '|   %s (development)'%_name)
            try: loadedPlugins.append(__import__( _name ))
            except: # invalid plugin
                import sys, traceback
                print(); traceback.print_exception(*sys.exc_info()); print()
    print()

def initPlugins():
    for pMod in loadedPlugins:
        for key,item in plugin.__dict__.items(): # supply these for Phase 3 w/o Phase 2
            if key.startswith('__'): continue
            pMod.__dict__[key]=item
        if 'ugeInitPlugin' in pMod.__dict__:
            print( 'Initializing %s'%pMod.__name__.split('.')[-1])
            pMod.ugeInitPlugin({})
    print()


class _walk(object): # Tcll - copied and improved from ast.NodeVisitor
    # noinspection PyUnresolvedReferences
    def __init__(this,tree):
        this.current_targets = {}
        this.visit_Call.__globals__['skw'] = modules['/struct()_keywords/'] # sets a direct reference
        this.visit_Call.__globals__['sn'] = modules['/struct()_names/']
        this.generic_visit(tree) # Tcll - make our instance work for us: _walk(tree)
        
    def visit_Assign(this, node): # Tcll - ast is so stupid, but it works (I don't think the python devs had any sort of focus on optimization here)
        current_targets = this.current_targets; current_targets.clear(); targets, value = node.targets[0], node.value
        if 'elts' in targets.__dict__ and 'elts' in value.__dict__: # tuple assign
            for _t,_v in zip(targets.elts, value.elts):
                if _v.__class__ == Call and hasattr(_v.func,'id') and _v.func.id == 'struct': current_targets[_v.args[0].s] = _t.id
        elif value.__class__ == Call and hasattr(value.func,'id') and value.func.id == 'struct': current_targets[value.args[0].s] = targets.id
        this.generic_visit(node)

    # noinspection PyUnresolvedReferences
    def visit_Call(this, node):
        if hasattr(node.func,'id') and node.func.id == 'struct':
            current_targets = this.current_targets
            sid = node.args[0].s
            sn[sid] = current_targets[sid] if sid in current_targets else ''
            skw[sid] = [kw.arg for kw in node.keywords]
        this.generic_visit(node)
        
    # Tcll - removed the unneeded visit() function in favor of direct implementation below (less CPU-steps taken)
    def generic_visit(self, node): # Called if no explicit visitor function exists for a node.
        for field in node._fields: # Tcll - made single-run from iterable dual-run (no longer doing 2.5x work)
            if not hasattr(node, field): continue
            value = getattr(node, field); cls = value.__class__ # Tcll - direct referencing is faster than attribute referencing
            if cls == list: [ getattr(self, 'visit_%s'%item.__class__.__name__, self.generic_visit)(item) for item in value if AST in item.__class__.__mro__ ]
            elif AST in cls.__mro__: getattr(self, 'visit_%s'%cls.__name__, self.generic_visit)(value)
            # Tcll - replaced isinstance() with __class__.__mro__ WOOT!

# noinspection PyBroadException,PyCompatibility
def loadLibraries(libDir = 'libs'):
    
    path.append(libDir)
    print( 'Loading Libraries:')
    ext = '.zip'
    for package in os.listdir(libDir):
        pkgpath='%s/%s'%(libDir.replace('\\','/'),package) # libs/lib.zip
        
        global src,mod # <- required for some reason, or NameError in modify()
        if os.path.isfile(pkgpath) and pkgpath.endswith(ext):
            if os.path.exists('%s/__init__.py'%pkgpath[:-len(ext)]): continue # skip if in-dev.
            _name=pkgpath.split('/')[-1][:-len(ext)]
            _file = '%s/%s/__init__.py'%(_name+ext,_name)
            _loader = zi(pkgpath)
            try:
                print( '|   %s'%_name)
                path.append(pkgpath)

                plg = modules[_name] = module(_name) # set the namespace
                plg.__dict__.update({
                    'UGE_MODEL_SCRIPT'      :CONST.UGE_MODEL_SCRIPT,
                    'UGE_ANIMATION_SCRIPT'  :CONST.UGE_ANIMATION_SCRIPT,
                    'UGE_IMAGE_SCRIPT'      :CONST.UGE_IMAGE_SCRIPT,
                    'UGE_PALETTE_SCRIPT'    :CONST.UGE_PALETTE_SCRIPT,
                    'UGE_COMPRESSION_SCRIPT':CONST.UGE_COMPRESSION_SCRIPT,
                    'UGE_ARCHIVE_SCRIPT'    :CONST.UGE_ARCHIVE_SCRIPT,
                    '__name__'              : _name,
                    '__package__'           : _name, # root
                    '__path__'              : [pkgpath],
                    '__file__'              : _file,
                    '__loader__'            : _loader
                    })
                plg.__dict__.update(CONST.UGE_MODEL_SCRIPT.NS) # TODO: need a library namespace for this stuff.

                # update src with array and struct IDs
                src = _loader.get_data(_file) # get the package's code
                mod = 0; notWhite,varchar = re.compile('[^ \\\t\n]'),re.compile('[_A-Za-z0-9]')
                def modify(offset,end): # "struct(-1)" --> "struct('RVL_IMG 153',-1)"
                    global src,mod; offset+=mod; end+=mod; pos=end+src[end:].find('(')
                    if pos<end or re.search(varchar,src[offset-1]) or re.search(notWhite,src[end:pos]): return
                    argStart=pos+1; ID="'%s %i',"%(_name,offset); mod+=len(ID); src="%s%s%s"%(src[:argStart],ID,src[argStart:])
                [modify(m.start(),m.end()) for m in re.finditer( re.compile('(struct|array)') ,src)]

                # update struct keyword library for this lib
                modules['/struct()_keywords/'] = {}  # { ID:['name','name2','name3'], ... }
                modules['/struct()_names/'] = {} # { ID:'name', ... }
                modules['/UGE_LibStructKWN/'][_name] = [ modules['/struct()_keywords/'], modules['/struct()_names/'] ]
                _walk(compile(src, _file, 'exec', PyCF_ONLY_AST))
                
                code = compile(src,_file,'exec') # FIXED: traceback stacks can now find the offending code
                exec( code, plg.__dict__ ) # fill the namespace

            except: # invalid lib
                import sys, traceback
                print( 'WARNING: %s failed to load:'%(_name))
                print(); traceback.print_exception(*sys.exc_info()); print()
                
        if os.path.exists('%s/__init__.py'%pkgpath):
            _name=pkgpath.split('/')[-1]
            _file = '%s/__init__.py'%pkgpath
            # sys.platform == 'win32': _file=_file.replace('/','\\')
            try:
                print( '|   %s (development)'%_name)
                
                # noinspection PyArgumentList
                plg = modules[_name] = module(_name) # set the namespace
                plg.__dict__.update({
                    'UGE_MODEL_SCRIPT'      : CONST.UGE_MODEL_SCRIPT,
                    'UGE_ANIMATION_SCRIPT'  : CONST.UGE_ANIMATION_SCRIPT,
                    'UGE_IMAGE_SCRIPT'      : CONST.UGE_IMAGE_SCRIPT,
                    'UGE_PALETTE_SCRIPT'    : CONST.UGE_PALETTE_SCRIPT,
                    'UGE_COMPRESSION_SCRIPT': CONST.UGE_COMPRESSION_SCRIPT,
                    'UGE_ARCHIVE_SCRIPT'    : CONST.UGE_ARCHIVE_SCRIPT,
                    '__name__'              : _name,
                    '__package__'           : _name, # root
                    '__file__'              : _file,
                    '__path__'              : [pkgpath]
                    })
                plg.__dict__.update(CONST.UGE_MODEL_SCRIPT.NS) # TODO: need a library namespace for this stuff.
                
                # update src with array and struct IDs
                nl = len(_name)
                with open(_file) as ifh: src = ifh.read() # get the package's code
                mod = 0; notWhite,varchar = re.compile('[^\\ \t\n]'),re.compile('[_A-Za-z0-9]')
                def modify(offset,end): # "struct(-1)" --> "struct('RVL_IMG 153',-1)"
                    global src,mod; offset+=mod; end+=mod; pos=end+src[end:].find('(')
                    if pos<end or re.search(varchar,src[offset-1]) or re.search(notWhite,src[end:pos]): return
                    argStart=pos+1; ID="'%s %i',"%(_name,offset); mod+=len(ID); src="%s%s%s"%(src[:argStart],ID,src[argStart:])
                [modify(m.start(),m.end()) for m in re.finditer( re.compile('(struct|array)') ,src)]
                
                # update struct keyword library for this lib
                modules['/struct()_keywords/'] = {}  # { ID:['name','name2','name3'], ... }
                modules['/struct()_names/'] = {} # { ID:'name', ... }
                modules['/UGE_LibStructKWN/'][_name] = [ modules['/struct()_keywords/'], modules['/struct()_names/'] ]
                _walk(compile(src, _file, 'exec', PyCF_ONLY_AST))
                
                code = compile(src,_file,'exec') # FIXED: traceback stacks can now find the offending code
                exec( code, plg.__dict__ ) # fill the namespace
                
            except: # invalid lib
                import sys, traceback
                print( 'WARNING: %s failed to load:'%_name)
                print(); traceback.print_exception(*sys.exc_info()); print()
    print()

'''
extdir = os.path.sep.join((os.path.dirname(__file__), 'ext'))
extbindir = os.path.sep.join((extdir, sys.argv[1], ''))

if sys.platform == 'win32':
    # set dll search path for extensions requiring externals
    os.environ['PATH'] = os.pathsep.join((os.environ['PATH'], extbindir ))

# load python modules
sys.path.append(extdir)

# load packed python modules:
types = ['egg','whl']
[ sys.path.append( extdir+zipmod ) for zipmod in os.listdir(extdir) if any([ zipmod.endswith(t) for t in types ])]
[ sys.path.append( extbindir+zipmod ) for zipmod in os.listdir(extbindir) if any([ zipmod.endswith(t) for t in types ])]
'''

# this registers the scope functions:
class register:
    def __init__(this,types,isFunc=True,Deprecated=False):
        this.types = [C for C in CONST.__dict__.values( ) if C.__class__.__name__ == 'UGE_Scope' ] if types == all else types
        this.isFunc = isFunc
        this.Deprecated = Deprecated
    def __call__(this,f):
        n = f.__name__
        if not f.__doc__ and not this.Deprecated: print('NOTICE: undocumented function %s.%s'%(f.__module__,n))
        for t in this.types: t.NS[n]=f
        return f

# a hackable wrapper for use with external applications (for example, knowing what functions are called at what times in SIDE)
UGE_GLOBAL_WRAPPER = lambda f:f

def init( load_extensions: bool = False ) -> None:
    """Initialize the API"""
    #import sys

    """
    log = open('tracer.log','wb'); write = log.write
    modules['/UGE_logger_spacer/'] = ''
    def tracer(func):
        def wrapper( *args, **kwargs ):
            cf = modules['API.FILE']._current
            
            fname = func.__name__
            datatype = hasattr(args[0],'__dereferenced__')
            
            label=''
            if 'label' in kwargs: lb = kwargs['label']; label = lb.keys()[0] if lb.__class__==dict else lb.__str__()
            
            if datatype: # pre
                name = args[0].__name__ if (fname=='__init__' or fname=='__call__') else fname
                recursive = 'struct' in name or 'array' in name
                if not recursive: recursive = hasattr(args[0],'__iter__')
                #if recursive: modules['/UGE_logger_spacer/'] = modules['/UGE_logger_spacer/'][:-1] + u'│├'
                    
            called = func( *args,**kwargs ) # call the function to update the object's defaults
            #if hasattr(called,'__value__'): print name, called.__addr__, called.__size, called.__value__
            
            #print fname
            if fname=='jump': write( bytes('\n> %08X        : jumped to 0x%08x%s'%(called,cf.offset,label)) )
            
            if datatype and hasattr(called,'__addr__'): # post
                cd = cf.data
                write( bytes('\n> %08X% 8s: %s<%s> read 0x%s as %s%s'%(
                    called.__addr__, '(%s)'%called.__size__,
                    modules['/UGE_logger_spacer/'],
                    '%s "%s"'%(called.__name__,called.__id__) if hasattr(called,'__id__') else called.__name__,
                    ''.join(map('%02X'.__mod__, cd[called.__addr__:called.__addr__+called.__size__])),
                    called.__value__, label
                )) )
                #if recursive: modules['/UGE_logger_spacer/'] = modules['/UGE_logger_spacer/'][:-2] + u'├'
                
            return called
        return wrapper
    #modules['/UGE_GLOBAL_WRAPPER/'] = tracer
    """

    from . import scripts
    # WARNING: must be loaded in order:
    if load_extensions:
        loadPlugins() # extends/uses the API
        # TODO: loadMods() # can modify anything in the API and available plugins
    loadLibraries() # used by scripts with extended access to the modified API
    scripts.load()

    # noinspection PyBroadException
    try:
        initPlugins()
        #scripts.clean() #remove PYC files
        
        #try: # try to get the viewer plugin
        #from data import VIEWER
        #VIEWER.Init()
        #except: # use console UI
        #    raise RuntimeError('console UI is not currently usable')
            
    except:
        import sys, traceback
        print(); traceback.print_exception(*sys.exc_info()); print()
        input('Press Enter to Exit')
    #log.close()