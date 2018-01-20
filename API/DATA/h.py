# -*- coding: utf8 -*-
from sys import modules # faster referencing for faster loading

from .. import FILE
from ..utilities import hashcolor
from . import define, UGE_DATATYPE as DT

UGE_GLOBAL_WRAPPER, register = modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']

def __update__(dt):
    cf = FILE._current; offset = dt.__addr__ if dt.__silent__ else cf.offset; val = 0
    for v in cf[offset:offset+dt.__size__][::pow(-1, not dt.__big__)]: val=(val<<8)|v
    dt.__value__=(('%s0%iX'%('%',dt.__size__<<1))%val) # '0FF8'
    if not dt.__silent__: dt.__silent__ = True; cf.offset+=dt.__size__

# noinspection PyUnusedLocal,PyUnboundLocalVariable
def _h_set_(dt, value, big=False): # NOTE: we don't want this to be directly accessable
    cf = FILE._current; dt.__value__ = value; dt.__big__ = big
    # TODO: this could be optimized:
    value=eval( '0x%s'%(value.replace('0x','').replace(' ','')) ) # '0x08f0'/'08 F0' -> 2288
    offset = dt.__addr__ if dt.__silent__ else cf.offset
    cf[offset:offset+dt.__size__] = [(value>>(i<<3))&255 for i in range(dt.__size__)][::pow(-1,big)]
    cf._update_instances(dt.__addr__,dt.__size__ ) # this will call dt.__update__

_bh_set_ = lambda dt, value: _h_set_(dt, value, big=True) # TODO: this could be faster (not wrapped)
# NOTE: ^ wrapped because 'b' means big-endian (no 'big' argument)
    
# NOTE: ^ saved memory, these functions are not re-created during runtime

# noinspection PyUnusedLocal
@register(all,False)
class h(object): # TODO: update to __new__ so the sub-class can actually be a sub-class of this.
    """UGE data struct for hexidecimal digits of specified byte sizes.
    usage:
    - data = h32() # read
    - data = h32( big = True ) # read big endian
    - h32( '0x FEF' ) # write
    - h32( '0x FEF', big = True ) # write big endian
    defining and using new types:
    - h5 = h(5); data = h5() # multi use
    - data = h(5)() # single use
    """
    __slots__=['__name__','__size__','__dereferenced__']
    def __init__(this, size, *args, **kwargs):
        this.__name__ = 'h(%i)'%size
        this.__size__=size
        this.__dereferenced__ = False # set externally by deref( addr, struct ) before this struct is called
        
    @UGE_GLOBAL_WRAPPER
    def __call__(this,value=None,big=False,*args,**kw):

        # TODO: python-magic methods
        # noinspection PyUnusedLocal,PyShadowingNames
        class H(DT): # sub-class to represent the value-type and supply the reference address.
            __slots__=['__name__','__addr__','__size__','__big__','__value__','__silent__','__color__']
            def __init__(dt,value,big,*args,**kw): # NOTE: '__call__' required by UGE_GLOBAL_WRAPPER
                dt.__name__ = this.__name__
                dt.__addr__ = FILE._current.offset
                dt.__size__ = this.__size__
                dt.__big__ = big
                dt.__value__ = 0
                dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
                dt.__color__ = hashcolor(this.__name__)
                if value.__class__ is int: value = hex(value)
                if value.__class__ is str: dt.__silent__ = False; _h_set_(dt, value, big) # write
                elif value==None or value==u'': dt.__silent__ = False; __update__(dt) # read
                FILE._current._register_instance(dt)
            __update__=__update__ # specifically set for cf._set_update (may likely change) 
            if this.__dereferenced__: set=_h_set_

        if hasattr( value, '__iter__' ):
            raise TypeError('iterable detected, please use array()()')
        return H(value,big)

define( 'h8'    , h(1)  )
define( 'h16'   , h(2)  )
define( 'h24'   , h(3)  )
define( 'h32'   , h(4)  )
define( 'h64'   , h(8)  )
define( 'h128'  , h(16) )

# noinspection PyUnusedLocal
@register(all,False)
class bh(object): # TODO: update to __new__ so the sub-class can actually be a sub-class of this.
    """UGE data struct for big endian hexidecimal digits of specified byte sizes.
    usage:
    - data = bf32() # read
    - bh32( '0x FEF' ) # write
    defining and using new types:
    - bh5 = bh(5); data = bf5() # multi use
    - data = bh(5)() # single use
    """
    __slots__=['__name__','__size__','__dereferenced__']
    def __init__(this, size, *args, **kwargs):
        this.__name__ = 'bh(%i)'%size
        this.__size__=size
        this.__dereferenced__ = False # set externally by deref( addr, struct ) before this struct is called
        
    @UGE_GLOBAL_WRAPPER
    def __call__(this,value=None,*args,**kw):

        # TODO: python-magic methods
        # noinspection PyUnusedLocal,PyShadowingNames
        class BH(DT): # sub-class to represent the value-type and supply the reference address.
            __slots__=['__name__','__addr__','__size__','__value__','__silent__','__color__']
            __big__ = True
            def __init__(dt,value,*args,**kw): # NOTE: '__call__' required by UGE_GLOBAL_WRAPPER
                dt.__name__ = this.__name__
                dt.__addr__ = FILE._current.offset
                dt.__size__ = this.__size__
                dt.__value__ = 0
                dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
                dt.__color__ = hashcolor(this.__name__)
                if value.__class__ is int: value = hex(value)
                if value.__class__ is str: dt.__silent__ = False; _bh_set_(dt, value) # write
                elif value==None or value==u'': dt.__silent__ = False; __update__(dt) # read
                FILE._current._register_instance(dt)
            __update__=__update__ # specifically set for cf._set_update (may likely change) 
            if this.__dereferenced__: set=_bh_set_

        if hasattr( value, '__iter__' ):
            raise TypeError('iterable detected, please use array()()')
        return BH(value)

define( 'bh8'   , bh(1)  )
define( 'bh16'  , bh(2)  )
define( 'bh24'  , bh(3)  )
define( 'bh32'  , bh(4)  )
define( 'bh64'  , bh(8)  )
define( 'bh128' , bh(16) )