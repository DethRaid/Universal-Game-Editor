# -*- coding: utf-8 -*-
from sys import modules # faster referencing for faster loading

from .. import FILE
from ..utilities import hashcolor

UGE_GLOBAL_WRAPPER, register = modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']

# noinspection PyUnusedLocal
def __update__(sub): pass # arrays don't need to be updated, only the data-types they reference

def _cmpStop(stop,result): # compares a stop-struct (list or tuple of UGE data-types) to a UGE struct or array result
    if hasattr(result,'__iter__'): # UGE struct or array
        if not stop: stop = [0]*len(result)
        return all( _cmpStop(s,r) for r,s in zip(result,stop) )
    return stop==None or stop==result

def _write(ds,data,big,create=True):
    if '__iter__' in ds.__class__.__dict__:
        if  big.__class__==bool: big =[big]*ds.__len__()
        return [_write(s,d,b,create) for s,d,b in zip(ds,data,big)]
    elif create:
        ds.__dereferenced__ = True
        S=ds(data,big=big)
        ds.__dereferenced__ = False
        return S
    else: ds.set(data,big); return ds

@UGE_GLOBAL_WRAPPER
@register(all,False)
class array(type):
    """
    UGE data-struct for arrays.
    
    NOTE: Due to major performance, tracking, and interpretation issues,
    list-based structures are no longer supported, and will raise a TypeError.
    (This does not apply to the stop-struct)
    
    settings:
    - struct: the data-struct, or augment to use for each step of the array.
    - stop: (default: None) a comparator value to stop on the return value (None in iterables stops on any value)
    - count: (default: None) an int, data-struct, or augment to mark the length of the array (overrides `stop`)
    - offset: (default: None) an int, data-struct, or augment telling marking the data location
    - relation: (default: None) an int, data-struct, or augment applying a relative location to `offset`
    - map: (default: None) a function to apply to the return value
    
    usage:
    - data = array( bu8 )() # read a 0-terminated byte-array
    - data = array( bu16, stop=16384 )() # read an array of bu16 values terminated by 0xFFFF
    - data = array( bu32, count=4 )() # read an array of 4 bu32 values
    - data = array( bu32, count=bu32 )() # read a static-sized array of bu32 values
    - data = array( struct( 4, d1=bu16, d2=bu8, d3=bu8 ), stop=[ None, 0, 255 ] )() # read an array terminated by the stop-struct
    - data = array( bu32, count=bu32, offset=0 )() # read a static-sized array of bu32 values at the start of the memory space.
    - data = array( bu32, count=bu32 )( offset=0 ) # same as above using the override.
    - data = array( bu32, count=bu32, offset=bu32 )() # read a static-sized array at the given offset in the memory space.
    - data = array( bu32, count=bu32, offset=bu32, relation=bu32)() # same as above in relation to the given location.
    
    defining and using new types:
    - bu8arr = array( bu8, count=bu32 ); bu8arr()
    
    automation:
    - struct( Data = array( bu8, count=bu32, offset=bu32 ), )
    
    special features:
    - data = array( vec3, count=bu32, map=normalize )() # maps normalize( value ) to the vec3 value before appending it to the array.
    """
    __slots__ = []
    # noinspection PyUnusedLocal,PyMissingConstructor
    def __init__(this,__ID__, struct, stop=None, count=None, offset=None, relation=None, map=None): pass
    def __new__(this,__ID__, struct, stop=None, count=None, offset=None, relation=None, map=None):
        # struct: can be a UGE data-type object, or iterable containing UGE data-types
        # stop: can be a UGE data-type object, or iterable containing UGE data-types
        # count: can be a UGE data-type object, or python int type
        # offset: can be a UGE data-type object, or python int type
        # relation: can be a UGE data-type object, or python int type
        # map: can be any callable object supporting at least 1 argument
        
        _ds = struct
        
        # these names are too royal to attempt the jump into the __init__ scope below,
        # so they're constructing a telepad to give to the other names for them to be summoned once they reach their destination.
        _telepad = (stop,count)
        
        _offset = offset
        
        this.__color__ = hashcolor( __ID__ )
        
        def _array_set_( dt, value, big=False ):  # NOTE: we don't want this to be directly accessable
            cf = FILE._current
            if dt.__silent__: last = cf.offset; cf.offset = dt.__addr__
            for dt, data in zip( dt.__value__, value ): _write( _ds, data, big, False)
            if dt.__silent__: cf.offset = last
            else: dt.__silent__ = True
            ##cf._set_update(sub.__addr__,sub.__size__) # this will update all data-type objects within sub's data range
            # ^ not needed due to struct.set() calling cf._set_update() for it's own size range (covering the struct in segments)
            # ^ left in case things change (which is likely)
        
        if not callable(_ds):
            raise TypeError('The struct argument must be a UGE data struct or augment.')
        
        # noinspection PyShadowingNames,PyUnboundLocalVariable,PyUnresolvedReferences
        def __init__( dt, value=None, offset=None, big=False, label=''):
            cf = FILE._current
            
            # now that the other names have made it to their destination,
            # they place the telepad and the royal names appear before them to finish their journey.
            stop,count = _telepad
            # the other names want to pummel these names for their actions, but don't because of their royalty.
            
            if stop==None: stop = 0 # we cannot skip every struct

            if offset == None: offset = _offset # allow local-override
            if callable(offset): offset=offset()
            if hasattr(offset,'__value__'): offset=offset.__value__
            if relation: offset=offset+relation if offset else relation
            if offset!=None: last = cf.offset; cf.offset=long(offset)
            dt.__addr__ = cf.offset
            
            dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished

            subLabel=''
            if label.__class__==dict: label,subLabel = label.items()[0]
            
            _val = dt.__value__ = []
            dt.__len__ = _val.__len__
            dt.__getitem__ = _val.__getitem__
            dt.__iter__ = _val.__iter__
            app,pop=_val.append,_val.pop
            
            iterableSDT = hasattr(_ds,'__iter__')
            if value==None: # read data
                if callable(count):count = count() # UGE data-types/augments
                if hasattr(count,'__value__'): count = count.__value__ # UGE data-type instances
                if count.__class__ in (int,long): # counted (no stop-struct)
                    for i in range(count):
                        data = _ds( big=big, label=subLabel)
                        app( map( data ) if map else data )
                else: # until stop-struct
                    while True: # TODO: need to properly remove the stop-struct because cf._set_update will update the data-types (performance and memory issue)
                        data = _ds( big=big, label=subLabel ) # WARNING: the stop value still exists in pointer memory
                        if stop==None or (_cmpStop( stop, data.__value__ ) if iterableSDT else data==stop): break
                        app( map( data ) if map else data )

            elif hasattr(value,'__iter__'): # write data
                if callable(count): count(value.__len__()) # write struct count before array data
                [ app(_write(_ds,dataStruct,big)) for dataStruct in value]
                if stop!=None: app(_write(_ds,stop,big)) # write stop-struct after array data

            dt.__size__ = cf.offset-dt.__addr__
            if offset!=None: cf.offset=last # return to previous location

            if dt.__dereferenced__: dt.set=_array_set_

            cf._register_instance(dt)
            
        # done for SIDE, just so they're accessable like everything else. (this doesn't actually work above)
        __init__.func_globals['stop'] = stop
        __init__.func_globals['count'] = count

        return type.__new__( this, 'ARRAY', (object,), dict(
            __slots__=['__addr__','__size__','__value__','__silent__','__len__','__getitem__','__iter__','set'],
            __add__=lambda dt,o: dt.__value__+o, __radd__=lambda dt,o: o+dt.__value__,
            __repr__ = lambda dt: repr(dt.__value__), __str__ = lambda dt: str(dt.__value__),
            __init__=UGE_GLOBAL_WRAPPER(__init__), __id__=__ID__, __color__=this.__color__, __name__='array', 
            __dereferenced__=False, __update__=__update__ ) )
        