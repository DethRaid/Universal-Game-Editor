# -*- coding: utf8 -*-
from sys import modules, exc_info

from . import CWD, PyCF_ONLY_AST, CONST, _walk
from .utilities import timer
import os, traceback, re # TODO: use the faster, better designed, regex module

loading = False
current = None
scope = None

###########################################################################################
# scope definitions
###########################################################################################

from io import BytesIO, StringIO
import math

scopes = '''
    UGE_MODEL_SCRIPT
    UGE_MATERIAL_SCRIPT
    UGE_SHADER_SCRIPT
    UGE_IMAGE_SCRIPT
    UGE_PALETTE_SCRIPT
    UGE_ANIMATION_SCRIPT
    UGE_COMPRESSION_SCRIPT
    UGE_ARCHIVE_SCRIPT
'''.split()
# future:
'''
    UGE_LOGIC_SCRIPT
    UGE_CODE_SCRIPT
'''

class registry(object):
    def __init__(this):
        this.types = {} # { type: { scriptName, ... }, ... }
        this.scripts = {} # { scriptName: { libName, ... }, ... }
        this.descriptions = {} # { scriptName: { description: [ extension, ... ], ... }, ... }

# noinspection PyBroadException,PyUnresolvedReferences
class UGE_Scope(object):
    """this defines a restricted namespace (or scope) to execute a script with.
    current usage is to define what types of data a script can handle."""
    
    def __init__(scope,name):
        scope.__name__ = name
        scope.NS = {}
        #scope.NS['ugePoll%s'%scope.__name__[4:-7].capitalize()] = lambda:False
        # { scriptName, ... }
        scope.import_registry = registry()
        scope.export_registry = registry()
    
    def Import(scope, name):
        scopeType = scope.__name__[4:-7].capitalize()
        func_name = 'ugeImport%s'%scopeType; poll_name = 'ugePoll%s'%scopeType
        for script,libs in [(name,scope.import_registry.scripts[name])] if name else scope.import_registry.scripts.items():
            # credit to Gribouillis on DaniWeb for an earlier design: (it helped me work on this design)
            NameSpace = dict(scope.NS) # copy
            
            modules[ '/struct()_keywords/' ], modules[ '/struct()_names/' ] = {}, {}  # new temporary spaces
            
            structkeywords, structnames = modules[ '/UGE_ScriptStructKWN/' ][ script ]
            modules[ '/struct()_keywords/' ].update( structkeywords )
            modules[ '/struct()_names/' ].update( structnames )
            
            # TODO: only apply items (functions, vars, etc.) registered with the scope
            for lib in libs:
                NameSpace.update(modules[lib].__dict__)
                libstructkeywords, libstructnames = modules[ '/UGE_LibStructKWN/' ][ lib ]
                modules[ '/struct()_keywords/' ].update( libstructkeywords )
                modules[ '/struct()_names/' ].update( libstructnames )
            
            try: 
                mod_dict = modules[script].__dict__
                
                # TODO: operate on copy of current root (if an errors occur, the copy will be discarded)
                
                if not name: # specified script should disregard polling
                    if poll_name not in mod_dict: continue
                    poll_result = FunctionType( mod_dict[poll_name].__code__, NameSpace )()
                    for types in FILE._current._types: types[:] = [] # clear unused data-types
                    FILE._current.offset = 0 # reset the offset
                    if not poll_result: continue
                    
                print('executing %s-import script "%s"...'%(scopeType.lower(),script))
                time=timer()
                
                FunctionType( mod_dict[func_name].__code__, NameSpace )( FILE._current._name.split('.')[-1], None )
                
                time.checkpoint()
                
                # TODO: apply copy to current root
                
                break
            except:
                print(); traceback.print_exception(*exc_info()); print()
        modules[__name__].clean()
        
    def Export(scope, name):
        func_name = 'ugeExport%s'%scope.__name__[4:-7].capitalize()
        for script,libs in [name] if name else scope.export_registry.scripts.items():
            # credit to Gribouillis on DaniWeb for an earlier design: (it helped me work on this design)
            NameSpace = dict(scope.NS) # copy
            # TODO: only apply items (functions, vars, etc.) registered with the scope
            for lib in libs: NameSpace.update(modules[lib].__dict__)
            try:
                # TODO: operate on copy of current root (if an errors occur, the copy will be discarded)
                FunctionType( modules[script].__dict__[func_name].__code__, NameSpace )(
                    FILE._current._name.split('.')[-1], None )
                # TODO: apply copy to current root
                break
            except: print(); traceback.print_exception(*exc_info()); print()

CONST.define( scopes, UGE_Scope)

modules['/UGE_ScriptStructKWN/']={}
modules['/UGE_LibStructKWN/']={}

###########################################################################################
# script header functions
###########################################################################################

# noinspection PyShadowingNames
def ugeScriptType( scope ):
    global loading
    if loading: globals()['scope'] = scope

def ugeScriptFormats( types ):
    global loading, current, scope
    if loading:
        scopeType = scope.__name__[4:-7].capitalize()
        module_dict = modules[ current ].__dict__
        importable = 'ugeImport%s'%scopeType in module_dict
        exportable = 'ugeExport%s'%scopeType in module_dict
        if importable:
            import_types = scope.import_registry.types
            scope.import_registry.descriptions[ current ] = dict(types)
            scripts = scope.import_registry.scripts
            if current not in scripts: scripts[ current ] = set()
        if exportable:
            export_types = scope.export_registry.types
            scope.export_registry.descriptions[ current ] = dict(types)
            scripts = scope.export_registry.scripts
            if current not in scripts: scripts[ current ] = set()
        for description, extensions in types.items():
            for ext in extensions:
                if importable:
                    if ext not in import_types: import_types[ext] = { current }
                    else: import_types[ext].add( current )
                if exportable:
                    if ext not in export_types: export_types[ext] = { current }
                    else: export_types[ext].add( current )

def ugeScriptLibs( libs ):
    global loading, current, scope
    if loading:
        for lib in libs:  # assert all libs are registered and available.
            if lib not in modules:
                raise ImportError( "specified library '%s' is not available" )
        scopeType = scope.__name__[4:-7].capitalize()
        module_dict = modules[ current ].__dict__
        if 'ugeImport%s'%scopeType in module_dict: scope.import_registry.scripts[ current ] = set(libs)
        if 'ugeExport%s'%scopeType in module_dict: scope.export_registry.scripts[ current ] = set(libs)

###########################################################################################
# script loader
###########################################################################################

# noinspection PyGlobalUndefined,PyBroadException
def reload(name=None):
    """reload any changes made to the existing scripts"""
    global loading, current
    bad = []
    for scriptName in [name] if name else os.listdir('scripts'):
        if scriptName.endswith('.py'): # only get .py files
            loading = False; current = scriptName[:-3]
            try:
                path = '%sscripts/%s'%(CWD,scriptName)
                
                if current in modules: script = modules[current]
                else:
                    print('Registered script: %s.py'%current)
                    script = modules[current] = module(current) # set the namespace
                    script.__dict__.update(dict( {scopeName:CONST.__dict__[scopeName] for scopeName in scopes},
                        __file__ = path, __name__ = current,
                        __builtins__=modules['__builtin__'],
                        #object=object,
                        ugeScriptType = ugeScriptType,
                        ugeScriptFormats = ugeScriptFormats,
                        ugeScriptLibs = ugeScriptLibs,
                        BytesIO=BytesIO,
                        StringIO=StringIO,
                        math=math,
                        label=lambda value: None ))
                    
                global src,mod # <- required for some reason, or NameError in modify()
                with open(path) as ifh: src = ifh.read() # get the script's code
    
                # update src with array and struct IDs
                # NOTE: offending escape is not redundant, it checks for '\\' where used in python code
                mod = 0; notWhite,varchar = re.compile( "[^ \\\t\n]" ),re.compile( "[_A-Za-z0-9]" )
                def modify(offset,end): # "struct(-1)" --> "struct('Module_Name 153',-1)"
                    global src,mod; offset+=mod; end+=mod; pos=end+src[end:].find('(')
                    if pos<end or re.search(varchar,src[offset-1]) or re.search(notWhite,src[end:pos]): return
                    argStart=pos+1; ID="'%s %i',"%(current,offset); mod+=len(ID); src="%s%s%s"%(src[:argStart],ID,src[argStart:])
                [modify(m.start(),m.end()) for m in re.finditer( re.compile('(struct|array)') ,src)]
                
                modules['/struct()_keywords/'] = {}  # { ID:['name','name2','name3'], ... }
                modules['/struct()_names/'] = {} # { ID:'name', ... }
                modules['/UGE_ScriptStructKWN/'][current] = [ modules['/struct()_keywords/'], modules['/struct()_names/'] ]
                
                _walk(compile(src, path, 'exec', PyCF_ONLY_AST))
                
                source = compile(src,path,'exec') # FIXED: traceback stacks can now find the offending code
                exec( source, script.__dict__ ) # fill the namespace
                loading = True
                exec( source, script.__dict__ ) # add to the collection
                
            except: # execution failed likely because of a syntax error
                print(); traceback.print_exception(*exc_info()); print()
                print('Unregistered script: %s.py'%current)
                bad.append(current)
                for scopeName in scopes:
                    Scope = CONST.__dict__[ scopeName ]
                    
                    if current in Scope.import_registry.scripts: del Scope.import_registry.scripts[current]
                    for scripts in Scope.import_registry.types.values():
                        if current in scripts: scripts.remove(current)
                    if current in Scope.import_registry.descriptions: del Scope.import_registry.descriptions[current]
                    
                    if current in Scope.export_registry.scripts: del Scope.export_registry.scripts[current]
                    for scripts in Scope.export_registry.types.values():
                        if current in scripts: scripts.remove(current)
                    if current in Scope.export_registry.descriptions: del Scope.export_registry.descriptions[current]
                del modules[current]
            
    return bad

# noinspection PyShadowingNames
def load( show=True ):
    print('Loading scripts...')
    bad = reload()
    if show:
        print('Support:')
        scopesLen = scopes.__len__()-1
        for scopeIndex,scopeName in enumerate(scopes):
            scopeEnd = scopeIndex == scopesLen
            scope = CONST.__dict__[ scopeName ]
            scopeType = scopeName[ 4:-7 ].capitalize( )
            print( u'├ ugeImport%s'%scopeType )
            scriptsLen = scope.import_registry.scripts.__len__()-1
            for scriptIndex,script in enumerate(scope.import_registry.scripts):
                print( u'│ %s %s'%(u'├└'[ scriptIndex == scriptsLen ], script) )
            if scriptsLen>-1: print(u'│')
            print( u'%s ugeExport%s' % (u'├└'[ scopeEnd ], scopeType) )
            scopeEndChar = u'│ '[ scopeEnd ]
            scriptsLen = scope.export_registry.scripts.__len__()-1
            for scriptIndex,script in enumerate(scope.export_registry.scripts):
                print( u'%s %s %s' % (scopeEndChar, u'├└'[ scriptIndex == scriptsLen ], script) )
            if not scopeEnd and scriptsLen>-1: print( u'│')
        if bad:
            print( '\nBad Scripts' )
            badLen = bad.__len__()-1
            for badIndex,script in enumerate(bad):
                print( u'%s %s'%(u'├└'[ badIndex==badLen ], script) )
        print()

def clean(): # delete the pyc files in the scripts directory
    for script in os.listdir('scripts'):
        if script[:-4]=='.pyc':
            try: os.remove('scripts/%s'%script)
            except OSError: pass

# noinspection PyUnresolvedReferences
from . import DATA, LOGIC, FILE, FORMAT
#from .DATA.u import FILE # link to initialized to avoid ghosting (API.scripts.FILE vs API.DATA.u.FILE)