# -*- coding: utf8 -*-
from sys import modules # faster referencing for faster loading

from .. import FILE
from ..utilities import hashcolor
from . import define, UGE_DATATYPE as DT#, readonly as RO

UGE_GLOBAL_WRAPPER, register = modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']


def __update__(dt):
    cf = FILE._current; offset = dt.__addr__ if dt.__silent__ else cf.offset; val = 0
    for v in cf[offset:offset+dt.__size__][::pow(-1, not dt.__big__)]: val=(val<<8)|v
    dt.__value__=val
    if not dt.__silent__: dt.__silent__ = True; cf.offset+=dt.__size__

def _u_set_(dt, value, big=False): # NOTE: we don't want this to be directly accessable
    cf = FILE._current; dt.__value__ = value; dt.__big__ = big
    offset = dt.__addr__ if dt.__silent__ else cf.offset
    cf[offset:offset+dt.__size__] = [(value>>(i<<3))&255 for i in range(dt.__size__)][::pow(-1,big)]
    cf._update_instances(dt.__addr__,dt.__size__ ) # this will call dt.__update__

_bu_set_ = lambda dt, value: _u_set_(dt, value, big=True) # TODO: this could be faster (not wrapped)
# NOTE: ^ wrapped because 'b' means big-endian (no 'big' argument)
    
# NOTE: ^ saved memory, these functions are not re-created during runtime

# noinspection PyUnusedLocal
@register(all,False)
class u(object): # TODO: update to __new__ so the sub-class can actually be a sub-class of this.
    """UGE data struct for unsigned ints of specified byte sizes.
    usage:
    - data = u32() # read
    - data = u32( big = True ) # read big endian
    - u32( 1536 ) # write
    - u32( 1536, big = True ) # write big endian
    defining and using new types:
    - u5 = u(5); data = u5() # multi use
    - data = u(5)() # single use
    """
    __slots__=['__name__','__size__','__dereferenced__']
    def __init__(this, size, *args, **kwargs):
        this.__name__ = 'u(%i)'%size
        this.__size__=size
        this.__dereferenced__ = False # set externally by deref( addr, struct ) before this struct is called
            
    @UGE_GLOBAL_WRAPPER
    def __call__(this,value=None,big=False,*args,**kw):

        # TODO: python-magic methods
        # TODO: validate value-size range (e.g.: size:2, min:0, max:65535)
        # noinspection PyUnusedLocal,PyShadowingNames
        class U(DT): # sub-class to represent the value-type and supply the reference address.
            __slots__=['__name__','__addr__','__size__','__big__','__value__','__silent__','__color__']
            def __init__(dt,value,big,*args,**kw): # NOTE: '__call__' required by UGE_GLOBAL_WRAPPER
                dt.__name__ = this.__name__
                dt.__addr__ = FILE._current.offset
                dt.__size__ = this.__size__
                dt.__big__ = big
                dt.__value__ = 0
                dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
                dt.__color__ = hashcolor(this.__name__)
                if value.__class__ == float: value = int(value)
                if value.__class__ is int: dt.__silent__ = False; _u_set_(dt, value, big) # write
                elif value==None or value==u'': dt.__silent__ = False; __update__(dt) # read
                FILE._current._register_instance(dt)
            __update__=__update__ # specifically set for cf._set_update (may likely change) 
            if this.__dereferenced__: set=_u_set_
            '''
            __lt__ = lambda dt,o: dt.__value__<o
            __le__ = lambda dt,o: dt.__value__<=o
            __eq__ = lambda dt,o: dt.__value__==o
            __ne__ = lambda dt,o: dt.__value__!=o
            __gt__ = lambda dt,o: dt.__value__>o
            __ge__ = lambda dt,o: dt.__value__>=o

            __cmp__ = lambda dt,o: dt.__value__.__cmp__(o)
            __hash__ = lambda dt: dt.__value__.__hash__()
            __nonzero__ = lambda dt: dt.__value__.__nonzero__()
            __index__ = lambda dt: dt.__value__.__index__()
            __add__ = lambda dt,o: dt.__value__.__add__(o)
            __sub__ = lambda dt,o: dt.__value__.__sub__(o)
            __mul__ = lambda dt,o: dt.__value__.__mul__(o)
            __div__ = lambda dt,o: dt.__value__.__div__(o)
            __truediv__ = lambda dt,o: dt.__value__.__truediv__(o)
            __floordiv__ = lambda dt,o: dt.__value__.__floordiv__(o)
            __mod__ = lambda dt,o: dt.__value__.__mod__(o)
            __divmod__ = lambda dt,o: dt.__value__.__divmod__(o)
            __pow__ = lambda dt,o: dt.__value__.__pow__(o)
            __lshift__ = lambda dt,o: dt.__value__.__lshift__(o)
            __rshift__ = lambda dt,o: dt.__value__.__rshift__(o)
            __and__ = lambda dt,o: dt.__value__.__and__(o)
            __xor__ = lambda dt,o: dt.__value__.__xor__(o)
            __or__ = lambda dt,o: dt.__value__.__or__(o)
            __radd__ = lambda dt,o: dt.__value__.__radd__(o)
            __rsub__ = lambda dt,o: dt.__value__.__rsub__(o)
            __rmul__ = lambda dt,o: dt.__value__.__rmul__(o)
            __rdiv__ = lambda dt,o: dt.__value__.__rdiv__(o)
            __rtruediv__ = lambda dt,o: dt.__value__.__rtruediv__(o)
            __rfloordiv__ = lambda dt,o: dt.__value__.__rfloordiv__(o)
            __rmod__ = lambda dt,o: dt.__value__.__rmod__(o)
            __rdivmod__ = lambda dt,o: dt.__value__.__rdivmod__(o)
            __rpow__ = lambda dt,o: dt.__value__.__rpow__(o)
            __rlshift__ = lambda dt,o: dt.__value__.__rlshift__(o)
            __rrshift__ = lambda dt,o: dt.__value__.__rrshift__(o)
            __rand__ = lambda dt,o: dt.__value__.__rand__(o)
            __rxor__ = lambda dt,o: dt.__value__.__rxor__(o)
            __ror__ = lambda dt,o: dt.__value__.__ror__(o)
            __neg__ = lambda dt: dt.__value__.__neg__()
            __pos__ = lambda dt: dt.__value__.__pos__()
            __abs__ = lambda dt: dt.__value__.__abs__()
            __invert__ = lambda dt: dt.__value__.__invert__()
            __int__ = lambda dt: dt.__value__.__int__()
            __float__ = lambda dt: dt.__value__.__float__()
            __oct__ = lambda dt: dt.__value__.__oct__()
            __hex__ = lambda dt: dt.__value__.__hex__()
            __str__ = lambda dt: dt.__value__.__str__()
            __repr__ = lambda dt: dt.__value__.__repr__()

            __iadd__=__isub__=__imul__=__idiv__=__itruediv__=__ifloordiv__=__imod__=__ipow__=\
            __ilshift__=__irshift__=__iand__=__ixor__=__ior__=RO
            '''
        if hasattr( value, '__iter__' ):
            raise TypeError('iterable detected, please use array(%s)()'%this.__name__)
        return U(value,big)

define( 'ubyte u8'  , u(1)  )
define( 'ushort u16', u(2)  )
define( 'u24'       , u(3)  )
define( 'uword u32' , u(4)  )
define( 'udword u64', u(8)  )
define( 'u128'      , u(16) )

# noinspection PyUnusedLocal
@register(all,False)
class bu(object): # TODO: update to __new__ so the sub-class can actually be a sub-class of this.
    """UGE data struct for big endian unsigned ints of specified byte sizes.
    usage:
    - data = bu32() # read
    - bu32( 1536 ) # write
    defining and using new types:
    - bu5 = bu(5); data = bu5() # multi use
    - data = bu(5)() # single use
    """
    __slots__=['__name__','__size__','__dereferenced__']
    def __init__(this, size, *args, **kwargs):
        this.__name__ = 'bu(%i)'%size
        this.__size__=size
        this.__dereferenced__ = False # set externally by deref( addr, struct ) before this struct is called
    
    @UGE_GLOBAL_WRAPPER
    def __call__(this,value=None,*args,**kw):

        # TODO: python-magic methods
        # TODO: validate value-size range (e.g.: size:2, min:0, max:65535)
        # noinspection PyUnusedLocal,PyShadowingNames
        class BU(DT): # sub-class to represent the value-type and supply the reference address.
            __slots__=['__name__','__addr__','__size__','__value__','__silent__','__color__']
            __big__ = True
            def __init__(dt,value,*args,**kw): # NOTE: '__call__' required by UGE_GLOBAL_WRAPPER
                dt.__name__ = this.__name__
                dt.__addr__ = FILE._current.offset
                dt.__size__ = this.__size__
                dt.__value__ = 0
                dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
                dt.__color__ = hashcolor(this.__name__)
                if value.__class__ == float: value = int(value)
                if value.__class__ is int: dt.__silent__ = False; _bu_set_(dt, value) # write
                elif value==None or value==u'': dt.__silent__ = False; __update__(dt) # read
                FILE._current._register_instance(dt)
            __update__=__update__ # specifically set for cf._set_update (may likely change) 
            if this.__dereferenced__: set=_bu_set_
            '''
            __lt__ = lambda dt,o: dt.__value__<o
            __le__ = lambda dt,o: dt.__value__<=o
            __eq__ = lambda dt,o: dt.__value__==o
            __ne__ = lambda dt,o: dt.__value__!=o
            __gt__ = lambda dt,o: dt.__value__>o
            __ge__ = lambda dt,o: dt.__value__>=o

            __cmp__ = lambda dt,o: dt.__value__.__cmp__(o)
            __hash__ = lambda dt: dt.__value__.__hash__()
            __nonzero__ = lambda dt: dt.__value__.__nonzero__()
            __index__ = lambda dt: dt.__value__.__index__()
            __add__ = lambda dt,o: dt.__value__.__add__(o)
            __sub__ = lambda dt,o: dt.__value__.__sub__(o)
            __mul__ = lambda dt,o: dt.__value__.__mul__(o)
            __div__ = lambda dt,o: dt.__value__.__div__(o)
            __truediv__ = lambda dt,o: dt.__value__.__truediv__(o)
            __floordiv__ = lambda dt,o: dt.__value__.__floordiv__(o)
            __mod__ = lambda dt,o: dt.__value__.__mod__(o)
            __divmod__ = lambda dt,o: dt.__value__.__divmod__(o)
            __pow__ = lambda dt,o: dt.__value__.__pow__(o)
            __lshift__ = lambda dt,o: dt.__value__.__lshift__(o)
            __rshift__ = lambda dt,o: dt.__value__.__rshift__(o)
            __and__ = lambda dt,o: dt.__value__.__and__(o)
            __xor__ = lambda dt,o: dt.__value__.__xor__(o)
            __or__ = lambda dt,o: dt.__value__.__or__(o)
            __radd__ = lambda dt,o: dt.__value__.__radd__(o)
            __rsub__ = lambda dt,o: dt.__value__.__rsub__(o)
            __rmul__ = lambda dt,o: dt.__value__.__rmul__(o)
            __rdiv__ = lambda dt,o: dt.__value__.__rdiv__(o)
            __rtruediv__ = lambda dt,o: dt.__value__.__rtruediv__(o)
            __rfloordiv__ = lambda dt,o: dt.__value__.__rfloordiv__(o)
            __rmod__ = lambda dt,o: dt.__value__.__rmod__(o)
            __rdivmod__ = lambda dt,o: dt.__value__.__rdivmod__(o)
            __rpow__ = lambda dt,o: dt.__value__.__rpow__(o)
            __rlshift__ = lambda dt,o: dt.__value__.__rlshift__(o)
            __rrshift__ = lambda dt,o: dt.__value__.__rrshift__(o)
            __rand__ = lambda dt,o: dt.__value__.__rand__(o)
            __rxor__ = lambda dt,o: dt.__value__.__rxor__(o)
            __ror__ = lambda dt,o: dt.__value__.__ror__(o)
            __neg__ = lambda dt: dt.__value__.__neg__()
            __pos__ = lambda dt: dt.__value__.__pos__()
            __abs__ = lambda dt: dt.__value__.__abs__()
            __invert__ = lambda dt: dt.__value__.__invert__()
            __int__ = lambda dt: dt.__value__.__int__()
            __float__ = lambda dt: dt.__value__.__float__()
            __oct__ = lambda dt: dt.__value__.__oct__()
            __hex__ = lambda dt: dt.__value__.__hex__()
            __str__ = lambda dt: dt.__value__.__str__()
            __repr__ = lambda dt: dt.__value__.__repr__()

            __iadd__=__isub__=__imul__=__idiv__=__itruediv__=__ifloordiv__=__imod__=__ipow__=\
            __ilshift__=__irshift__=__iand__=__ixor__=__ior__=RO
            '''
        if hasattr( value, '__iter__' ):
            raise TypeError('iterable detected, please use array(%s)()'%this.__name__)
        return BU(value)

define( 'bubyte bu8'    , bu(1)  )
define( 'bushort bu16'  , bu(2)  )
define( 'bu24'          , bu(3)  )
define( 'buword bu32'   , bu(4)  )
define( 'budword bu64'  , bu(8)  )
define( 'bu128'         , bu(16) )