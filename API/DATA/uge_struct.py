# -*- coding: utf8 -*-
from sys import modules # faster referencing for faster loading

from .. import FILE
from ..utilities import hashcolor

UGE_GLOBAL_WRAPPER, register = modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']

'''
>>> class t(object):
	def __getitem__(this, key): print key

	
>>> i = t()
>>> i['test']
test
>>> i[0]
0
>>> i[0:5]
slice(0, 5, None)
>>> i['test','test2']
('test', 'test2')
>>> i['test':'test5']
slice('test', 'test5', None)
>>> i[0:5,5:6]
(slice(0, 5, None), slice(5, 6, None))
>>> 
'''
# noinspection PyUnusedLocal
def __update__(dt): pass # structs don't need to be updated, only the data-types they reference

@register(all,False)
class struct(type):
    """Defines a UGE data-struct.
    
    usage:
    - myStruct = struct( -1, data = bu32, value = bf32 ) # (default) determines the byte-size (8) from read data.
    - myStruct = struct( 12, data = bu32, value = bf32 ) # specific byte-size of 12, reading 8 and skipping the rest.
    - myStruct = struct( -1, data = bu32, value = bf32 if version<2 else None ) # None ignores the attribute
    
    - Data = myStruct() # read all
    - Data = myStruct( big = True ) # read all in big endian
    - Data = myStruct( [ 1536, 2.5 ] ) # write all
    - Data = myStruct( [ 1536, 2.5 ], big = True ) # write all in big endian
    
    features:
    
    data, value = Data
    value, data = Data[ 1, 0 ]
    (value),(data) = Data[ 1:, :1 ]
    value, data = Data[ 'value', 'data' ]
    data = Data.data
    """
    __slots__ = []
    def __init__( __this__, __ID__, *args, **kw ): pass # not used (at all), just needs args to match __new__
    def __new__( __this__, __ID__, *args, **kw ): # credit to Gribouillis for the base-code
        argLen = len(args)
        _size = args[0] if argLen else -1
        _offset = args[1] if argLen>1 else None
        name = modules['/struct()_names/'][__ID__]
        _order = modules['/struct()_keywords/'][__ID__] # TODO: use a registry for these (not hacks), and track changes.
        datatypes = [kw[n] for n in _order]
        
        __this__.__color__ = hashcolor( __ID__ )
        
        for attr in _order: # attribute safety
            if len(attr)>4 and attr.startswith('__') and attr.endswith('__'):
                raise AttributeError( "`__private__` attributes are not allowed in UGE structs" )
            if attr=='set':
                raise AttributeError( "`set` is reserved for dereferenced UGE structs" )
        
        def _structset_(dt, value, big=False): # NOTE: we don't want this to be directly accessable
            cf = FILE._current
            if dt.__silent__: last = cf.offset; cf.offset = dt.__addr__
            for attr,v in zip(_order,value):
                st = dt.__dict__[attr]
                st.__silent__ = False # we don't need to jump, we did that above
                st.set(v)
            if dt.__silent__: cf.offset = last
            else: dt.__silent__ = True
            ##cf._set_update(sub.__addr__,sub.__size__) # this will update all data-type objects within sub's data range
            # ^ not needed due to dt.set() calling cf._set_update() for it's own size range (covering the struct in segments)
            # ^ left in case things change (which is likely)

        # noinspection PyUnusedLocal
        def __init__(dt,value=None,offset=None,big=False,label='', *_args, **_kw): # this is called dynamically
            cf = FILE._current
            
            #print(dt.__class__.__color__)
            
            #dt.__class__.__color__.__set__(dt, __this__.__color__)
            
            dt.__size__ = _size() if callable(_size) else _size
            if offset == None: offset = _offset # allow local-override
            if callable(offset): offset=offset()
            if hasattr(offset,'__value__'): offset=offset.__value__
            #if _relation: offset+=_relation
            if offset!=None: last = cf.offset; cf.offset=long(offset)
            dt.__addr__ = cf.offset
            if dt.__dereferenced__: dt.set=_structset_
            
            OL = len(_order) # Tcll - not sure why this works here when this doesn't work in the array() data-struct
            
            labels=''
            if label.__class__==dict: label,labels = label.items()[0]
            if labels.__class__ is str: labels=[labels]*OL
            if labels.__class__ not in (list,tuple): labels=['']*OL
            LL = len(labels)
            if LL<OL: labels.extend(['']*(OL-LL))

            values = [None]*OL

            _val = dt.__value__ = []
            dt.__iter__ = _val.__iter__
            app = _val.append
            
            _get = dt.__class__.__dict__.__getitem__ # using descriptors faster :)
            dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
            for attr, subtype, value, lbl in zip(_order,datatypes,values,labels[:OL]):
                if not subtype: _get(attr).__set__(dt,None); app(None); continue
                subtype.__dereferenced__ = True
                data = subtype(value,label=lbl); _get(attr).__set__(dt,data); app(data)
                subtype.__dereferenced__ = False
            if _size>0: cf.offset = dt.__addr__+_size
            elif _size==-1: dt.__size__ = cf.offset-dt.__addr__ # determine struct size from post file offset
            if offset!=None: cf.offset=last # return to previous location
            
            cf._register_instance(dt)
            
            # because SIDE's tracer can't find these globals
            __init__.__globals__['datatypes'] = datatypes
            __init__.__globals__['keywords'] = _order # redefined as something easier to understand
            
        # Tcll - I keep forgetting, so here's some notes for myself:
        # __this__ = struct() # includes the sub-class along with the struct instance
        # dt = __this__() #( called to read from the file and set local attributes )
        # sub2 = deref( ref(sub), this ) # applies the .set() method to sub2 (instance of this)
        
        def __getitem__(dt, item): # this['item'] or this[0] or this[1:7:2] or this['item1','item2']
            # Tcll - would be nice if this magic function had better documentation to tell me exactly how to use it (IDK how lists set their index)
            # falling back to operating on `order`
            T = item.__class__
            if T==tuple: return map( dt.__getitem__, item) # dt[ item1, item2, ... ] return the corresponding attribute values
            if T==slice: return map( dt.__getitem__, _order[item]) # dt[ 1:2[, 0:4:2] ] return sets of indexed attribute values (see notes below for details)
            if T is int : return dt.__value__[item] # dt[ 1[, 3] ] return indexed attribute values
            if T is str: return dt.__dict__.__dict__[item].__get__(dt) # dt[ 1[, 3] ] return keyed attribute values (just like a dictionary)
        
        #def __setitem__(sub, item, value): # ^ = value
        #def __delitem__(sub, item): # del this[item]

        def __repr__(sub): return ('struct( %i,\n%s)'%( _size, ''.join(['%s = %s,\n'%(attr,val) for attr,val in zip(_order,sub.__value__)]) )).replace('\n','\n    ')
        
        return type.__new__( __this__, name, (object,), dict(
            __slots__ = ['__addr__','__size__','__value__','__silent__','__iter__','set']+_order,
            __init__=UGE_GLOBAL_WRAPPER(__init__), __len__=_order.__len__, __getitem__=__getitem__, __repr__=__repr__,
            __lt__=lambda dt,other: dt.__value__ < other,
            __le__=lambda dt,other: dt.__value__ <= other,
            __eq__=lambda dt,other: dt.__value__ == other,
            __ne__=lambda dt,other: dt.__value__ != other,
            __gt__=lambda dt,other: dt.__value__ > other,
            __ge__=lambda dt,other: dt.__value__ >= other,
            __id__=__ID__, __name__=("struct '%s'" % name if name else 'struct'),
            __dereferenced__=False, __update__=__update__
        ))

''' NOTES:
Examples of file R/W actions and how they work:

ex = struct( -1, # default (ignore padding)
    a1=bu32,
    a2=bu32,
    a3=bu32,
    a4=bu32,
    a5=bu32,
    a6=bu32,
    a7=bu32,
    a8=bu32
)

vals = ex() # read
vals = ex([0,0,0,0,0,0,0,0]) # write (writing 0's is also called allocation)

# --- attribute access --- :

# - reading:
print( vals.a1 )

# - writing:
vals.a1.set( 2048 )

# --- alternative attribute access --- :

# - reading:
print( vals['a1'] )

# - writing:
vals['a1'].set( 2048 )

# --- advanced attribute access --- :

# - reading:
print( vals['a1','a2','a5'] )

# - writing: ( TODO: simplify via returning a setter object instead of a tuple)
for a,v in zip( vals['a1','a2','a5'], [0,0,0] ): a.set( v )
# NOTE: ^ this will still work in the future

# - future plans:
    # - writing: (done right)
    vals['a1','a2','a5'].set( [0,0,0] )

    # --- keyed attribute sets --- :

    # - reading:
    (a1,a3,a5,a7),(a3,a4,a5) = vals[ 'a1':'a7':2, 'a3':'a5' ]
    
    # - writing:
    vals[ 'a1':'a3':2, 'a3':'a4' ].set( [0,0], [0,0] )
    
# --- indexed attribute access --- : (compatible with older methods)

# - reading:
print( vals[0] )

# - writing:
vals[0].set( 2048 )

# --- advanced indexed attribute access --- :

# - reading:
print( vals[0,3,4] )

# - writing: ( TODO: simplify via returning a setter object instead of a tuple)
for a,v in zip( vals[0,3,4], [0,0,0] ): a.set( v )
# NOTE: ^ this will still work in the future

# - future plans:
    # writing: (done right)
    vals[0,3,4].set( [0,0,0] )
    
# --- indexed attribute sets --- :

# - reading:
(a1,a3,a5,a7),(a3,a4,a5) = vals[ 0:7:2, 2:5 ]
    
# - writing: ( TODO: simplify via returning a setter object instead of a tuple of tuples)
for set,values in zip( vals[ 0:3:2, 2:4 ], [ [0,0], [0,0] ] ):
    for a,v in zip( set, values ): a.set( v )
# NOTE: ^ this will still work in the future.

# - future plans:
    # - writing:
    vals[ 0:3:2, 2:4 ].set( [0,0], [0,0] )


# --- dereferenced --- :

vpointer = ref( vals )

vals2 = deref( vpointer, ex ) # read

vals2.set( [15,0,0,0,0,0,0,0] ) # write/update
# NOTE: ^ this actually works as a dereferenced pointer and updates `vals` along with
# any data-type objects referencing from the offset range of `vals2.__addr__` spanning `vals2.__size__`
# (the same thing happens when any RAM-addressed data is updated in a C program)

# also note that a struct already dereferences all of it's contained data-types when read.
# for automation purposes, all dereferenced data-types have the .set() method



Examples of comparisons and how they work:

# - used when `vals` may not always be a struct-type: (with extra verification to make sure `ex` really is a struct)
if type(vals) == ex and type(ex) == struct:
# NOTE: `vals.__class__` is much faster than `type(vals)`

# - UGE-specific:

# - used when `vals` may be among different struct-types:
switch( len(vals) )
if case( 8 ):
if case( 2,3 ):

or

switch( vals.__class__ )
if case( ex ):
if case( vec2,vec3 ): # NOTE: future data-types

'''