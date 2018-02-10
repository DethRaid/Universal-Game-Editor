# -*- coding: utf8 -*-

# private imports:
from array import array
import sys,os
from sys import modules

#from .utilities import intType

UGE_GLOBAL_WRAPPER,register=modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']
FILE = modules[__name__]

global data # MEM.data descriptor: data.__get__(this); data.__set__(this,value)
newlist = lambda v: []
class MEM(object):
    """Virtual memory for data blocks, includes pointer support (not related to RAM)"""
    
    __slots__ = ['data','offset', '_types', '_parent', '_children', '_name', '_dir', '_id',
        '__len__','__getitem__']
    def __init__(this,path,ID,temp=False):
    
        data = array('B') # Tcll - fastest possible memory-safe array for filedata management
        MEM.__dict__['data'].__set__(this,data)
        this.__len__ = data.__len__
        this.__getitem__ = data.__getitem__
        this.offset = 0
        
        # here's the pointer-system's base:
        this._types = [] # [ [ data-type, ... ] ][ address ] # Tcll - possible MemoryError? >.>
        # NOTE: ^ the length must the same as `data`
    
        # MEM links for archives (might not be used)
        this._parent = None
        this._children = []

        this._dir,this._name = os.path.split(path)
        this._dir = this._dir.replace('\\','/')+(u'/' if this._dir else u'')
        #this._name = unicode(this._name)
        this._id = ID
        if temp: this._dir=None
        FILE._file.update({ this._name:this, this._id:this })

    #def preread(this,length): return this.data[this.offset:this.offset+length]
    #def read(this,length): d=this.data[this.offset:this.offset+length]; this.offset+=length; return d
    def alloc(this,size): # save up some memory before writing (speed things up a bit)
        this._types.extend( map( newlist, range(size) ) )
        this.data[this.offset:this.offset+size]=array('B',[0])*size
        if this._types.__len__()!=this.data.__len__():
            raise BufferError('pointer buffer size does not match data buffer size')
    '''
    def write(this,data,cls):
        if data.__class__ in (int,long): # single byte
            this.data[this.offset:this.offset+1] = array('B',[data])
            if this.offset==this.__len__(): this._types.append( [] )
        else:
            try: # byte array (any ordered iterable with byte-values)
                filelen = this.__len__(); datalen = data.__len__(); maxlen = this.offset+datalen
                this.data[this.offset:maxlen] = array('B',data)
                if maxlen>filelen: this._types.extend( map(newlist, range( maxlen - filelen ) ) )
            except:
                raise Exception( 'FATAL: `%s` supplied MEM.write() with innumerable data.'%cls )
    '''
    # Tcll - this is the secret to how the pointer system tracks and maintains file-data updates across data-type instances.
    def _update_instances( this, address, size ):
        """updates the value of every data-type using these addresses."""
        updated = []
        for types in this._types[address:address+size]:
            for dt in types:
                if dt in updated: continue # we've updated this data-type already
                dt.__update__()
                updated.append(dt)
        while updated: updated.pop( )  # clear the machine memory for other operations (unlink data-types from here)

    def _adust_addresses( this, address, size, modifier ):
        """adjusts the __addr__ of every data-type above address+size by the modifier."""
        adjusted = []
        for types in this._types[address+size:]:
            for dt in types:
                if dt in adjusted: continue # we've adjusted this data-type already
                if dt.__addr__==address: continue # this data-type is at the root and should not be moved
                dt.__addr__+=modifier
                adjusted.append(dt)
        if modifier<0: this._types[address+size+modifier:] = this._types[address+size:]
        if modifier>0: this._types[address+size:address+size] = [
            # Tcll - I could probably use something better than list comprehension here >.>
            # NOTE: this is supposed to copy the data types in the list, not the list itself.
            list(this._types[(address+size)-1].__iter__()) for i in range(modifier)]
            # NOTE: copying could cause possible dereferencing issues with certain data-types >.>
        while adjusted: adjusted.pop() # clear the machine memory for other operations (unlink data-types from here)

    def _register_instance( this, dt ): # Tcll - I have a feeling this can be optimized better... >.>
        """registers our newly created (or perhaps referenced) data-type for dereferencing"""
        range_min, range_max = dt.__addr__, dt.__addr__+dt.__size__
        bounds = this._types.__len__()-1
        if range_min > bounds:
            raise BufferError('data-type address 0x%08X out of bounds 0x%08X'%(range_min,bounds))
        if range_max > bounds:
            raise BufferError('data-size at 0x%08X exceeds bounds 0x%08X'%(range_max,bounds))
        for addr in range(dt.__addr__,dt.__addr__+dt.__size__):
            types = this._types[addr]
            if dt not in types: types.append(dt)
    
    def __setitem__(this, item, value):
        this.data[ this.offset:this.offset + 1 ] = array( 'B', value ) # NOTE: __get__, not __set__ (__setattr__)
        tlen,dlen = this._types.__len__(),this.data.__len__()
        if tlen<dlen: this._types[tlen:dlen] = map(newlist,range(dlen-tlen))
    
    def __setattr__(this, key, value):
        if key=='data':
            raise AttributeError('attribute `data` is not writable.')
        MEM.__dict__[key].__set__(this,value) # this should not call this function

data = MEM.data


_master = None # mainly used to retrieve the master-file's directory for resource-files (open for future plans)
_previous = None # mainly used for switching files
_current = None # filesystem state-engine operation
_file = {} # returns the MEM() instance referenced by both name and id
_FID = 0 # fix for file removal ID issue (ID is maintained for new files)

# Tcll - I've had issues with `globals()['var'] = True` throwing a NameError when referencing `var` afterwards
# and don't even get me started with issues related to `global var; var = True`, I'm done playing around with this keyword.
# and to add, the other methods are easier to both read and use.


def _ClearFiles(): FILE._file.clear(); FILE._FID=0; FILE._current=None; FILE._master=None
written=[]
# noinspection PyBroadException
def _WriteFiles():
    global written
    md = FILE._master._dir
    for identifier,f in FILE._file.items():
        n = f._name; fd = f._dir
        if n in written: continue
        written.append(n)
        if fd==None: continue # Temp file
        if md not in fd: fd = '%s/%s'%(md,fd)
        try: os.makedirs(fd)
        except: pass

        with open(fd+n,'wb') as F:
            PrP,sec=0,(1.0/(len(f.data)-1))*100
            for i,c in enumerate(f.data.tostring()):
                F.write(c); P=int(sec*i)
                if P!=PrP: sys.stdout.write(' \rexporting %s %i%s'%(n,P,'%')); PrP=P
            sys.stdout.write(' \rexporting %s %s\n'%(n,'100%'))

    FILE._ClearFiles()
    written=[]

@UGE_GLOBAL_WRAPPER
@register(all)
def alloc(size):
    """
    allocates (reserves) memory for the data you're about to write.
    (speeds up processing by updating buffered values rather than creating them)
    """
    if size.__class__ is int: FILE._current.alloc(size)
    else:
        raise TypeError('an int is required')

'''
# noinspection PyUnusedLocal
class _PAD(object):
    def __init__(this,regname):
        this.__addr__ = 0; this.__name__ = regname; this.__dereferenced__=False
        sys.modules['/UGE_Type_Names/'][regname] = '_PAD()'
        
    @UGE_GLOBAL_WRAPPER
    def __call__(this, length, label='', *_args, **_kw):
        if length.__class__ in (int,long):
            cf = FILE._current
            if cf.offset<len(cf.data): return cf.read(length) # read
            else: cf.alloc(length) # write
        else:
            raise TypeError('an int is required')
    __call__.__globals__['FILE']=FILE

# Tcll - just to make this work: 9_9
def _set(f): f.__globals__['call'] = _PAD(f.__name__); return f
'''
# noinspection PyUnusedLocal
@UGE_GLOBAL_WRAPPER
@register(all)
def pad(length, *_args, **_kw):
    """read/write pad-bytes"""
    lcls = length.__class__
    if lcls == int: length = long( length ); lcls = long
    if lcls == long:
        cf = FILE._current
        if cf.offset<len(cf.data): return cf.read(length) # read
        else: cf.alloc(length) # write
    else:
        raise TypeError('an int is required')
    
# noinspection PyUnusedLocal
@UGE_GLOBAL_WRAPPER
@register(all)
def skip(length, *_args, **_kw):
    """skips the given number of bytes"""
    lcls = length.__class__
    if lcls == int: length = long( length ); lcls = long
    if lcls == long:
        cf = FILE._current
        if cf.offset<len(cf.data): return cf.read(length) # read
        else: cf.alloc(length) # write
    else:
        raise TypeError('an int is required')

# noinspection PyUnusedLocal
@UGE_GLOBAL_WRAPPER
@register(all)
def jump(offset, relation=0, position=0, label=''):
    """jumps to the given offset from the start or current file position at the given relation."""
    if callable(offset): offset = offset() # UGE data-struct or augment
    if hasattr(offset,'__value__'): offset = offset.__value__ # UGE data-type
    cf = FILE._current; dl = cf.__len__(); last = int(cf.offset)
    offset += relation+last if position else relation # current offset?
    #print u'> %08X        : jumped to 0x%08x%s'%(last,offset,label)
    if -dl<offset<dl: cf.offset = offset; return last # verify that we are w/in range of the memory space
    else: return None # TODO: need to log the error (jumping past end of file)

struct2addr = lambda s: s.__addr__ if '__addr__' in s.__dict__ else None
#@UGE_GLOBAL_WRAPPER
#@register(all)
def ref( *structs ): # stupidly simple pointer interface:
    """references the address(es) of the supplied data types.
    
    usage:
    - addr = ref( value ) # value being any UGE data type
    """
    return struct2addr(structs[0]) if len(structs)==1 else map(struct2addr,structs)

#@UGE_GLOBAL_WRAPPER
#@register(all)
def deref( struct, addr ):
    """de-references the address as the supplied data struct and returns the value at the address.
    
    usage:
    - value = deref( struct, addr ) # struct being any UGE data struct
    """
    cf = FILE._current
    if '__name__' in struct.__dict__ and struct.__name__ in modules['/UGE_Type_Names/']:

        dl = cf.__len__()
        if -dl<addr<dl:
            o = cf.offset; cf.offset = long(addr) # remember current offset and silent-jump to the reference location

            struct.__dereferenced__ = True # define the new struct representation with the set() attribute
            value = struct()
            struct.__dereferenced__ = False

            cf.offset = o  # restore current offset
            del o
            
            return value
        
        else: return None
        # TODO: ^need to log the error (we can only jump to a random address w/in the file range)
            
    else: return None # TODO: need to log the error (can't apply an unknown struct)

# File Handling Functions:

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeImportFile( path, scope=None, script=None, compression=None ):
    """Imports a file to virtual-space data.
    
    usage:
    - FileID = ugeImportFile( "subdirectory/FileName" )
    script operation: (execute scripts on imported data)
    - ugeImportFile( "...", scope=UGE_MODEL_SCRIPT ) # search based on extension
    - ugeImportFile( "...", scope=UGE_MODEL_SCRIPT, script='filename' )
    - ugeImportFile( FID, script=UGE_MODEL_SCRIPT ) # for ugeTempFile or dataspace
    """
    # cases to consider:
    # ugeImportFile( "image", UGE_MODEL_SCRIPT ) # auto-determine with ugePollModel
    # ugeImportFile( "image.jpg", UGE_MODEL_SCRIPT ) # png image (find if jpg polling fails)
    if path.__class__ == str: path = unicode( path )
    if path.__class__==unicode:
        from glob import glob
        path = path.replace( '\\', '/' ) # win paths to UGE paths
        if FILE._master and not path.startswith('/'): path = FILE._master._dir+path # relative to master file
        files = [path]
        if not os.path.exists(path): # let's find an existing path
            files = glob('%s.*'%path)
            files.sort() # files with no extension should be first
            if not files:
                raise IOError( "'%s' does not exist" % path ) # critical error
        
        for f in files:
            f = f.replace( '\\', '/' )  # win path to UGE path
            
            # TODO: save some memory by re-using the MEM instance.
            with open( f, 'rb' ) as stream:
                a = array('B',stream.read())
                FILE._previous = FILE._current
                cf = FILE._current = MEM( f, FILE._FID ); cf.alloc( a.__len__() ); FILE._FID+=1
                if FILE._master == None: FILE._master = cf
        
                # Tcll - I want a progress tracker (even if it's stupid)
                data,name = cf.data,cf._name # avoid the DOT operator in CPU-intensive areas
                PrP,sec=0,(1.0/(len(a)-1))*100
                for i,d in enumerate(a): # fill the data space
                    data[i] = d; P=int(sec*i)
                    if P!=PrP: sys.stdout.write(' \rimporting %s %i%s'%(name,P,'%')); PrP=P
                sys.stdout.write(' \rimporting %s %s\n'%(name,'100%'))
                del a
            
            if scope!=None:
                if scope.Import(script): return None
            else: break # automation cannot be performed here,
            # it's up to the invoking script to deal with the imported data.
        
        return FILE._current._id
    elif path.__class__ is int: # file or dataspace ID
        cf = FILE._current
        FILE._current = FILE._file[path]
        if scope!=None: scope.Import(script)
        FILE._current = cf
        return None
    else: pass # TODO: need to log the error (Path must be a str or unicode object)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeExportFile( Path ): 
    """Creates a file in virtual-space data to be exported.
    
    usage:
    - FileID = ugeExportFile( "subdirectory/FileName" )"""
    if Path.__class__==str:
        Path = Path.replace('\\','/') # win paths to UGE paths
        # TODO: export to master path
        cf = FILE._current = MEM( Path, FILE._FID ); FILE._FID+=1
        if FILE._master == None: FILE._master = cf
        return cf._id
    
    else: pass # TODO: need to log the error (Path must be a str or unicode object)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeTempFile( Name ):
    """Creates a temporary file in the virtual space.
    
    usage:
    - FileID = ugeTempFile( "FileName" )"""
    if Name.__class__==str:
        cf = FILE._current = MEM( Name, FILE._FID, True ); FILE._FID+=1; return cf._id
    else: pass # TODO: need to log the error (Name must a str or unicode object)

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_ARCHIVE_SCRIPT]) # only avalable for archives (this function is not final)
#def ugeInnerFile(script, mode, name=''): pass

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeSwitchFile(identifier=None):
    """Switches the active file to the previous or specified file.
    
    usage:
    - FileID = ugeSwitchFile( None ) # (default) previous file
    - FileID = ugeSwitchFile( 0 )
    - FileID = ugeSwitchFile( "FileName" )"""
    icl = identifier.__class__
    if icl in {int,str} and identifier in FILE._file:
        FILE._previous = FILE._current
        cf = FILE._current = FILE._file[identifier]; return cf._id
    if identifier == None:
        pf = FILE._previous; FILE._previous = FILE._current
        FILE._current = pf; return pf._id
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeRemoveFile(identifier):
    """Deletes the specified file.
    
    usage:
    - ugeRemoveFile( 0 )
    - ugeRemoveFile( "FileName" )"""
    if identifier.__class__==int: identifier = long(identifier)
    if identifier.__class__==str: identifier = unicode(identifier)
    if identifier.__class__ in (long,unicode) and identifier in FILE._file:
        cf = FILE._file[identifier]; FILE._file.pop(cf._name); FILE._file.pop(cf._id)
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

# mainly used to update the master file on import/export operations.
# Tcll - this may be enabled for scripts in the future for sub-file operation.
def ugeSetMasterFile(identifier):
    if identifier.__class__==int: identifier = long(identifier)
    if identifier.__class__==str: identifier = unicode(identifier)
    if identifier.__class__ in (long,unicode) and identifier in FILE._file: FILE._master = FILE._file[identifier]
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeGetFileID( Name=None ):
    """Returns the ID of the current or specified file.
    
    usage:
    - FileID = ugeGetFileID( None ) # (default) current file
    - FileID = ugeGetFileID( "FileName" )"""
    if Name.__class__==str: Name = unicode( Name )
    if Name.__class__ in (long,unicode) and Name in FILE._file: return FILE._file[Name ]._id
    elif Name==None: return FILE._current._id
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeGetFileName(identifier=None):
    """Returns the name of the current or specified file.
    
    usage:
    - Name = ugeGetFileName( None ) # (default) current file
    - Name = ugeGetFileName( 0 )
    - Name = ugeGetFileName( "FileName" )"""
    if identifier.__class__==int: identifier = long(identifier)
    if identifier.__class__==str: identifier = unicode(identifier)
    if identifier.__class__ in (long,unicode) and identifier in FILE._file: return FILE._file[identifier]._name
    elif identifier==None: return FILE._current._name
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeSetFileName(Name):
    """Renames the current file.
    
    usage:
    - ugeSetFileName( 0 )"""
    if Name.__class__==str: Name = unicode(Name)
    if Name.__class__==unicode: FILE._current._name = Name; FILE._file[Name] = FILE._file.pop(FILE._current._name)
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeGetFileOffset(identifier=None):
    """Returns the absolute offset of the current or specified file.
    
    usage:
    - Offset = ugeGetFileOffset( None ) # (default) current file
    - Offset = ugeGetFileOffset( 0 )
    - Offset = ugeGetFileOffset( "FileName" )"""
    if identifier.__class__==int: identifier = long(identifier)
    if identifier.__class__==str: identifier = unicode(identifier)
    if identifier.__class__ in (long,unicode) and identifier in FILE._file: return FILE._file[identifier].offset
    elif identifier==None: return FILE._current.offset
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeSetFileOffset(offset):
    """Sets the current file's absolute offset.
    
    usage:
    - ugeSetFileOffset( 0 )"""
    if offset.__class__==int: offset = long(offset)
    if offset.__class__==long: FILE._current.offset = offset
    else: pass # TODO: need to log the error (identifier must be the file name or ID)

@UGE_GLOBAL_WRAPPER
@register(all)
def ugeGetFileSize(identifier=None):
    """Returns the size of the current or specified file.
    
    usage:
    - Size = ugeGetFileSize( None ) # (default) current file
    - Size = ugeGetFileSize( 0 )
    - Size = ugeGetFileSize( "FileName" )"""
    if identifier.__class__==int: identifier = long(identifier)
    if identifier.__class__==str: identifier = unicode(identifier)
    if identifier.__class__ in (long,unicode) and identifier in FILE._file: return len(FILE._file[identifier].data)
    elif identifier==None: return len(FILE._current.data)
    else: pass # TODO: need to log the error (identifier must be the file name or ID)
