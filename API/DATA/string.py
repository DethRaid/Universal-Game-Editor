# -*- coding: utf8 -*-
from sys import modules # faster referencing for faster loading

from .. import FILE

UGE_GLOBAL_WRAPPER, register = modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']

#@UGE_GLOBAL_WRAPPER
@register(all,False)
class string(type): # NOTE: this class isn't exactly "advanced", however it does slightly more (with more planned) than just read and write strings.
    """UGE data struct for strings.
    usage:
    - data = string()() # read a 0-terminated string
    - data = string(';')() # read a string terminated by a semicolon
    - data = string(4)() # read a 4-byte string
    - data = string(bu8)() # read a string sized by a 1-byte value
    - data = string(4, offset=0)() # read a 4-byte string at the start of the memory space.
    - data = string(4)(offset=0) # same as above using the override.
    - data = string(bu8, offset=bu32)() # read a static-sized string at the give offset in the memory space.
    - data = string(bu8, offset=bu32, relation=bu32)() # same as above in relation to the given location.
    defining and using new types:
    - str8 = string(bu8); str8()
    automation:
    - struct( Name = string( bu8, offset = bu32 ), )
    special features:
    - encoding: string(code='cp932')() # read a cp932-encoded string
    """
    __slots__ = []
    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(this, dtype=chr(0), code=None, offset=None, relation=0): pass
    def __new__(this, dtype=chr(0), code=None, offset=None, relation=0):
        
        _offset=offset
        this.__color__ = 0xFFFF80

        # noinspection PyUnboundLocalVariable
        def __update__( dt ):
            cf = FILE._current
            if dt.__silent__: last = cf.offset; cf.offset = dt.__addr__
            val = ''.join( map( chr, cf[dt.__addr__:dt.__addr__+dt.__size__] ) )  # fastest average conversion from [115, 116, 114, 105, 110, 103] to 'string'
            dt.__value__ = bytes(val).decode(code) if code else val
            if dt.__silent__: cf.offset = last
            else: dt.__silent__ = True

        def _string_set_( dt, value, big=True ):  # NOTE: we don't want this to be directly accessable
            cf = FILE._current
            dataType = dtype
            
            if dt.__silent__: last = cf.offset; cf.offset = dt.__addr__
            if code is not None: value = value.encode(code)
            
            # add stop character: `string(stop)('string')`
            if  dataType.__class__  is str and len( dataType ) == 1: value += dataType
            
            #elif  dtype.__class__  is int: # `string(size)('string')`
            
            size = dt.__size__
            if size.__class__ is int: dt.__size__ = value.__len__()
            else: size.set(value.__len__())  # `string(u8)()` updates u8 with the new size
            
            old = int( size )
            cf[dt.__addr__:old] = value
            cf._adust_addresses( dt.__addr__, old, dt.__size__-old )  # 'oldstring' to 'string' or 'string' to 'newstring' (upper address adjustment)
            if dt.__silent__: cf.offset = last
            cf._update_instances( dt.__addr__, dt.__size__ )
        
        def __init__( dt, value=None, offset=None, label='', *args, **kwargs ):
            cf = FILE._current
            dataType = dtype
            
            dt.__big__=True # may be needed in the future, though unlikely
            dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
            
            if value == 0 or dataType == 0: # read entire file
                dt.__addr__ = 0 # forced
                dt.__value__= val = u''.join( map( chr, cf.data ) )
                dt.__size__ = val.__len__()
            
            if offset==None: offset=_offset # allow local-override
            if callable(offset): offset=offset()
            if hasattr(offset,'__value__'): offset=offset.__value__
            if relation: offset=offset+relation if offset else relation
            if offset!=None: last = cf.offset; cf.offset=int(offset)
            
            if value == None: # read
                _addr = dt.__addr__ = cf.offset
                
                if dataType == None: dataType = u'\x00' # safety first `string(None)()`
                
                if dataType.__class__ is str: # `string(stop)()`
                    val = ''.join( map( chr, cf.data[ _addr: _addr+cf[_addr:].index(ord(dataType)) ] ) ) # discard stop character
                    dt.__size__ = len(val ) + 1
                
                elif dataType.__class__ is int: # `string(size)()`
                    val = ''.join( map( chr, cf[_addr:_addr+dataType] ) ); dt.__size__ = dataType
                
                elif callable(dataType): # read size from file: `string(u8)()`
                    if offset!=None: cf.offset=offset # silent jump (for dataType())
                    dt.__size__ = dataType(); dt.__addr__=cf.offset # NOTE: cf.offset != offset due to dataType()
                    val = ''.join( map( chr, cf[_addr:_addr+dt.__size__] ) )
                
                dt.__value__ = bytes(val).decode(code) if code is not None else val
                cf.offset = dt.__addr__ + dt.__size__
                del val

            elif value.__class__ is int and value>0: # (override) read and return everything within the specified range
                _addr = dt.__addr__ = cf.offset
                
                val = ''.join( map( chr, cf[_addr:_addr+value] ) ); dt.__size__ = value # string()(size)
                if dataType.__class__ == str: # special case (PMD files): `string(stop)(size)` reads everything up to stop and skips the rest
                    if dataType in val: val = val[:val.index(dataType)] # note that sub.__size__ is still the full byte-width (do not change)
                
                dt.__value__ = bytes(val).decode(code) if code is not None else val
                cf.offset = dt.__addr__ + dt.__size__
                del val

            elif value.__class__ is str: # write
                if code is not None: value = value.encode(code)
                
                if dataType.__class__ is str and dataType.__len__()==1: value+=dataType # add stop character: `string(stop)('string')`
                #elif dataType.__class__ in (int,long): # `string(size)('string')`
                
                dt.__size__ = value.__len__()
                if callable(dataType): dataType(dt.__size__ ) # write size before string: `string(u8)('string')`
                dt.__addr__ = cf.offset
                
                cf[dt.__addr__:dt.__addr__+dt.__size__]=value
                cf.offset+=dt.__size__

            
            if offset!=None: cf.offset=last # return to previous location

            #if sub.__dereferenced__: sub.set=_stringset_
            cf._register_instance(dt)
        
        # Tcll - could probably optimize this more <_<
        # TODO: '__delattr__', '__getattribute__', '__getnewargs__', '__reduce__', '__reduce_ex__', '__setattr__', '__sizeof__'
        return type.__new__( this, 'string', (object,), dict(
            __slots__=['__addr__','__size__','__value__','__big__','__silent__','set'],
            __len__=lambda dt: dt.__value__.__len__(),
            __getitem__=lambda dt,item: dt.__value__[item],
            __iter__=lambda dt: dt.__value__.__iter__(),
            __add__=lambda dt, other: dt.__value__ + other, __radd__=lambda dt, other: other + dt.__value__,
            __mul__=lambda dt, other: dt.__value__ * other, __rmul__=lambda dt, other: other * dt.__value__,
            __mod__=lambda dt, other: dt.__value__ % other, __rmod__=lambda dt, other: other % dt.__value__,
            __contains__=lambda dt, item: dt.__value__.__contains__(item),
            __repr__=lambda dt: dt.__value__.__repr__(), __str__=lambda dt: dt.__value__.__str__(),
            __hash__=lambda dt: dt.__value__.__hash__(),
            __lt__=lambda dt, other: dt.__value__ < other,
            __le__=lambda dt, other: dt.__value__ <= other,
            __eq__=lambda dt, other: dt.__value__ == other,
            __ne__=lambda dt, other: dt.__value__ != other,
            __gt__=lambda dt, other: dt.__value__ > other,
            __ge__=lambda dt, other: dt.__value__ >= other,
            __format__=lambda dt,formatSpec: dt.__value__.__format__(formatSpec),
            center    =lambda dt,width,fillchar=' ': dt.__value__.center(width,fillchar),
            expandtabs=lambda dt,tabsize=8: dt.__value__.expandtabs(tabsize),
            decode    =lambda dt,encoding,errors='strict': dt.__value__.decode(encoding,errors),
            encode    =lambda dt,encoding,errors='strict': dt.__value__.encode(encoding,errors),
            format    =lambda dt,*args,**kwargs: dt.__value__.format(args,kwargs),
            lower     =lambda dt,: dt.__value__.lower(),
            upper     =lambda dt,: dt.__value__.upper(),
            capitalize=lambda dt,: dt.__value__.capitalize(),
            swapcase  =lambda dt,: dt.__value__.swapcase(),
            title     =lambda dt,: dt.__value__.title(),
            join      =lambda dt,sequence: dt.__value__.join(sequence),
            ljust     =lambda dt,width: dt.__value__.ljust(width),
            rjust     =lambda dt,width: dt.__value__.rjust(width),
            strip     =lambda dt,chars=None: dt.__value__.strip(chars),
            lstrip    =lambda dt,chars=None: dt.__value__.lstrip(chars),
            rstrip    =lambda dt,chars=None: dt.__value__.rstrip(chars),
            replace   =lambda dt,old,new_,maxsplit=-1: dt.__value__.replace(old,new_,maxsplit),
            translate =lambda dt,table,deletechars='': dt.__value__.translate(table,deletechars),
            zfill     =lambda dt,width: dt.__value__.zfill(width),
            split     =lambda dt,sep,maxsplit=None: dt.__value__.split(sep,maxsplit),
            rsplit    =lambda dt,sep,maxsplit=None: dt.__value__.rsplit(sep,maxsplit),
            splitlines=lambda dt,keepends=False: dt.__value__.splitlines(keepends),
            partition =lambda dt,sep:dt.__value__.partition(sep),
            rpartition=lambda dt,sep:dt.__value__.rpartition(sep),
            count =lambda dt,sub,start=None,end=None: dt.__value__.count( sub,start,end),
            find  =lambda dt,sub,start=None,end=None: dt.__value__.find(  sub,start=None,end=None),
            rfind =lambda dt,sub,start=None,end=None: dt.__value__.rfind( sub,start=None,end=None),
            index =lambda dt,sub,start=None,end=None: dt.__value__.index( sub,start=None,end=None),
            rindex=lambda dt,sub,start=None,end=None: dt.__value__.rindex(sub,start=None,end=None),
            startswith=lambda dt,prefix,start=None,end=None: dt.__value__.startswith(prefix,start,end),
            endswith  =lambda dt,suffix,start=None,end=None: dt.__value__.endswith(suffix,start,end),
            isalnum=lambda dt: dt.__value__.isalnum(),
            isalpha=lambda dt: dt.__value__.isalpha(),
            isdigit=lambda dt: dt.__value__.isdigit(),
            islower=lambda dt: dt.__value__.islower(),
            isspace=lambda dt: dt.__value__.isspace(),
            istitle=lambda dt: dt.__value__.istitle(),
            isupper=lambda dt: dt.__value__.isupper(),
            __init__=UGE_GLOBAL_WRAPPER( __init__ ),
            __color__=this.__color__, __name__='string', __dereferenced__=False, __update__=__update__ ) )

'''
class string(object): # NOTE: this class isn't exactly "advanced", however it does slightly more (with more planned) than just read strings.
    # Tcll - not quite sure how to use __slots__ = [], but I know it saves alot of memory per instance.
    # ^ (also results in slightly faster execution due to less RAM data being written per instance)
    
    #def __init__(this, dtype=None, start='', stop=chr(0), recursive=False, code=None):
    def __init__(this, dtype=chr(0), code=None, offset=None, relation=0):
        this.__name__ = 'string'
        
        this.__addr__ = 0 # future pointer support for ref()
        
        this.dtype = dtype
        this.code = code # encoding
        this.offset = offset # automation
        this.relation = relation # extended automation

    @UGE_GLOBAL_WRAPPER
    def __call__(this, value=None, offset=None, label='', *args, **kwargs):
        cf = FILE._current
        
        if value == 0: # (override)
            #_C._LOG("----DATA----: read file as string")
            this._size_ = len(cf.data); return bytearray(cf.data).__str__()

        if this.dtype == 0:
            #_C._LOG("----DATA----: read file as string")
            this._size_ = len(cf.data); return bytearray(cf.data).__str__()

        if offset==None: offset = this.offset # allow local-override
        if callable(offset): offset=offset()
        if this.relation: offset+=this.relation
        if value == None or value.__class__ == int: #read string
            adjust = offset == None

            currentposition = cf.offset
            if adjust: offset=currentposition
            #if _C._TOGGLE_LOGGING: l=_C._f[_C._c].__len__().__hex__().__len__()-2;p=(('0x%s0%ix'%('%',max(10,l)))%offset).upper()

            this.__addr__ = offset
            if value == None:
                if this.dtype == None: this.dtype = chr(0) # safety first
                if this.dtype.__class__ in (str,unicode):
                    _stop = ord(this.dtype)
                    d = cf.data[ offset: offset+cf.data[offset:].index(_stop)+1 ]
                    this._size_ = len(d); d = d[:-1] # discard stop character
                    #if _C._TOGGLE_LOGGING: end = ' to stop character "%s"'%chr(_stop)
                elif this.dtype.__class__ in (int,long):
                    d = cf.read( this.dtype ); this._size_ = this.dtype
                    #if _C._TOGGLE_LOGGING: end = ' of fixed length %i'%this.dtype
                elif callable(this.dtype): # read size from file
                    lo = cf.offset; cf.offset=offset # silent jump (for dtype())
                    this._size_ = this.dtype(); this.__addr__ = cf.offset
                    d = cf.read( this._size_ )
                    #if _C._TOGGLE_LOGGING: end = ' of static length %i'%this._size_
            elif value.__class__ in (int,long): # (override) read and return everything within the specified range
                this._size_ = value; d = cf.read( value )
                #if _C._TOGGLE_LOGGING: end = ' of specified length %i'%value
                if this.dtype.__class__ == str: # special case: string(stop)(size) returns everything up to stop (useful for fixed-size stop-terminated char arrays)
                    _stop = ord(this.dtype)
                    if _stop in d:
                        d = d[:d.index(_stop)]
                        #if _C._TOGGLE_LOGGING: end += ' to stop character "%s"'%chr(_stop)
                        
            cf.offset = currentposition+this._size_ if adjust else currentposition # do not adjust if using a specified offset.

            s = bytearray(d).__str__()
            #if _C._TOGGLE_LOGGING: _C._LOG("%s: read %sstring '%s'%s%s"%(p,('%s encoded '%this.code) if this.code else '',s,end,label))
            
            return s.decode(this.code) if this.code else s

        elif value.__class__ == str:
            #if this.code is not None: value = value.encode(code)
            this.__addr__ = cf.offset
            if this.dtype.__class__ in (str,unicode): value+=this.dtype
            if this.code is not None: value = value.encode('ascii')
            cf.data.extend(bytearray(value))
            this._size_ = len(value); cf.offset+=this._size_
            
    __call__.__globals__['FILE'] = modules['API.backend.FILE']
'''