# -*- coding: utf8 -*-
from sys import modules # faster referencing for faster loading

from .. import FILE, CONST
from ..utilities import hashcolor
from . import define, UGE_DATATYPE as DT

UGE_GLOBAL_WRAPPER, register = modules['/UGE_GLOBAL_WRAPPER/'],modules['/register/']

# noinspection PyCallingNonCallable
CONST.define( '''
        UGE_IEEE754
        UGE_IBM
        UGE_BORLAND
        '''.split(), type('UGE_Float_Type', (CONST.UGE_CONSTANT,), {}), [
            CONST.UGE_MODEL_SCRIPT,
            CONST.UGE_ANIMATION_SCRIPT,
            CONST.UGE_IMAGE_SCRIPT,
            CONST.UGE_PALETTE_SCRIPT,
            CONST.UGE_COMPRESSION_SCRIPT,
            CONST.UGE_ARCHIVE_SCRIPT ])
# NOTE: IBM and BORLAND format types are still being researched.
# here's Andrew's notes from HexEdit Pro:
''' IBM Floating Point Numbers

This numeric format is used in IBM mainframe and mini-computers and in many binary file formats.

The 32-bit format has a sign bit and a seven-bit exponent in the most significant byte (the left-most byte since these numbers are usually stored big-endian).
The exponent is a Excess-64 hexadecimal exponent which is equivalent to a nine bit binary exponent (since 16^128 = 2^512).
(See the Numbers section above for an explanation of Excess-X signed numbers.)

The remaining 24 bits are the mantissa.
Since the exponent is hexadecimal a normalised mantissa varies from any value greater than 0.0625 (1/16) to less than or equal to 1.0,
but non-normalised values are allowed (hence there is no implicit leading mantissa bit as in IEEE).

There is also a 64-bit format that is the same except for an extra 32 significant bits in the mantissa (giving a total of 56).
Since big-endian byte order is normally used this means a 64 bit values can just be treated as a 32 bit value.

There is also a 128 bit format but this is simply two consecutive 64 bit values which are simply added together.
The 2nd of the pair of values has an exponent which is always 14 less than the exponent in the 1st value which corresponds to 56 mantissa bits (16^14 = 2^56).
Hence this format has the same range of exponents as the 64 bit (and 32 bit) format but doubles the significant digits of the mantissa.
''' # Tcll - ^ I did not modify anything other than whitespace

# Tcll - I don't have anything on the Borland format yet

def __update__(dt):
    cf = FILE._current; offset = dt.__addr__ if dt.__silent__ else cf.offset; val = 0
    for v in cf[offset:offset+dt.__size__][::pow(-1, not dt.__big__)]: val=(val<<8)|v
    if val: # speedy check (before performing any unneeded calculations)
        # Tcll - credit to pyTony on Daniweb for simplifying the formula of 'e' and fixing most return values
        size = dt.__size__
        e=((size<<3)-1)//(size+1)+(size>2)*size//2; m,b=(((size<<3)-(1+e)), ~(~0 << e-1))
        S,E,M=((val>>((size<<3)-1))&1,(val>>m)&~(~0 << e),val&~(~0 << m))
        if E == ~(~0<<e): val=(float('NaN') if M!=0 else (float('+inf') if S else float('-inf')))
        else: val=((pow(-1,S)*(2**(E-b-m)*((1<<m)+M))) if E else pow(-1,S)*(2**(1-b-m)*M))
        dt.__value__=val
    else: dt.__value__ = 0.0
    if not dt.__silent__: dt.__silent__ = True; cf.offset+=dt.__size__

def _f_set_(dt, value, Format=CONST.UGE_IEEE754, big=False): # NOTE: we don't want this to be directly accessable
    cf = FILE._current; dt.__value__ = value; dt.__big__ = big
    if value: # speedy check (before performing any unneeded calculations)
        size = dt.__size__
        e=((size<<3)-1)//(size+1)+(size>2)*size//2+(size==3); m,E=(((size<<3)-(1+e)), ~(~0 << e-1)); S=0 # Tcll - formula by pyTony
        # Tcll - credit to jdaster64 on KC-MM:
        if value<0: S=1; value*=-1 #set the sign
        while value<1.0 or value>=2.0: value,E=(value*2.0,E-1) if value<1.0 else (value/2.0,E+1)
        value = (S<<(e+m))|(E<<m)|int(round((value-1)*(1<<m)))
    offset = dt.__addr__ if dt.__silent__ else cf.offset
    cf[offset:offset+dt.__size__] = [(value>>(i<<3))&255 for i in range(dt.__size__)][::pow(-1,big)]
    cf._update_instances(dt.__addr__,dt.__size__ ) # this will call dt.__update__

_bf_set_ = lambda dt, value, Format=CONST.UGE_IEEE754: _f_set_(dt, value, Format, big=True) # TODO: this could be faster (not wrapped)
# NOTE: ^ wrapped because 'b' means big-endian (no 'big' argument)
    
# NOTE: ^ saved memory, these functions are not re-created during runtime

# noinspection PyUnusedLocal
@register(all,False)
class f(object): # TODO: update to __new__ so the sub-class can actually be a sub-class of this.
    """UGE data struct for floats of specified byte sizes.
    usage:
    - data = f32() # read
    - data = f32( big = True ) # read big endian
    - f32( -15.36 ) # write
    - f32( -15.36, big = True ) # write big endian
    defining and using new types:
    - f5 = f(5); data = f5() # multi use
    - data = f(5)() # single use
    """
    __slots__=['__name__','__size__','__dereferenced__']
    def __init__(this, size, *args, **kwargs):
        this.__name__ = 'f(%i)'%size
        this.__size__=size
        this.__dereferenced__ = False # set externally by deref( addr, struct ) before this struct is called
        
    @UGE_GLOBAL_WRAPPER
    def __call__(this,value=None,Format=CONST.UGE_IEEE754,big=False,*args,**kw):

        # TODO: python-magic methods
        # TODO: validate value precision
        # TODO: take floating-point precision away from the CPU via operations to the long(exponent) and long(mantissa)
        # noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
        class F(DT): # sub-class to represent the value-type and supply the reference address.
            __slots__=['__name__','__addr__','__size__','__big__','__value__','__silent__','__color__','signbit','exponent','mantissa']
            def __init__(dt,value,big,*args,**kw): # NOTE: '__call__' required by UGE_GLOBAL_WRAPPER
                dt.__name__ = this.__name__
                dt.__addr__ = FILE._current.offset
                dt.__size__ = this.__size__
                dt.__big__ = big

                # future: (to replace dt.__value__ for faster and almost unrestricted (up to highest long()) operations)
                dt.signbit = None
                dt.exponent = None
                dt.mantissa = None
                # Tcll - ^ everything I look at seems to follow this base format in some form or another
                # (for example, nintendo int vectors supply the exponent in the attributes,
                # while the mantissa and optional sign are supplied throughout the int vectors)
                # ^ NOTE: the method to process the actual value though differs from these, and is far simpler.

                dt.__value__ = 0
                dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
                dt.__color__ = hashcolor(this.__name__)
                if intType(value.__class__): value = float(value)
                if value.__class__ == float: dt.__silent__ = False; _f_set_(dt, value, Format, big) # write
                elif value==None or value==u'': dt.__silent__ = False; __update__(dt) # read
                FILE._current._register_instance(dt)
            __update__=__update__ # specifically set for cf._set_update (may likely change) 
            if this.__dereferenced__: set=_f_set_

        if hasattr( value, '__iter__' ):
            raise TypeError('iterable detected, please use array()()')
        return F(value,Format,big)

define( 'f8'        , f(1)  )
define( 'half f16'  , f(2)  ) # NOTE: don't confuse this with half-int aka short.
define( 'f24'       , f(3)  )
define( 'f32'       , f(4)  )
define( 'double f64', f(8)  )
define( 'f128'      , f(16) ) # also called a double-double

# noinspection PyUnusedLocal
@register(all,False)
class bf(object): # TODO: update to __new__ so the sub-class can actually be a sub-class of this.
    """UGE data struct for big endian floats of specified byte sizes.
    usage:
    - data = bf32() # read
    - bf32( -15.36 ) # write
    defining and using new types:
    - bf5 = bf(5); data = bf5() # multi use
    - data = bf(5)() # single use
    """
    __slots__=['__name__','__size__','__dereferenced__']
    def __init__(this, size, *args, **kwargs):
        this.__name__ = 'bf(%i)'%size
        this.__size__=size
        this.__dereferenced__ = False # set externally by deref( addr, struct ) before this struct is called
            
    @UGE_GLOBAL_WRAPPER
    def __call__(this,value=None,Format=CONST.UGE_IEEE754,*args,**kw):

        # TODO: python-magic methods
        # TODO: validate value precision
        # TODO: take floating-point precision away from the CPU via operations to the long(exponent) and long(mantissa)
        # noinspection PyUnusedLocal,PyShadowingNames,PyUnresolvedReferences
        class BF(DT): # sub-class to represent the value-type and supply the reference address.
            __slots__=['__name__','__addr__','__size__','__value__','__silent__','__color__','signbit','exponent','mantissa']
            __big__ = True
            def __init__(dt,value,*args,**kw): # NOTE: '__call__' required by UGE_GLOBAL_WRAPPER
                dt.__name__ = this.__name__
                dt.__addr__ = FILE._current.offset
                dt.__size__ = this.__size__

                # future: (to replace dt.__value__ for faster and almost unrestricted operations)
                dt.signbit = None
                dt.exponent = None
                dt.mantissa = None
                # Tcll - ^ everything I look at seems to follow this format in some form or another
                # (for example, nintendo int vectors supply the exponent in the attributes,
                # while the mantissa and optional sign are supplied throughout the int vectors)
                # ^ NOTE: the method to process the actual value though differs from these, and is far simpler.

                dt.__value__ = 0
                dt.__silent__ = True # used to update a dereferenced location (silent jump) and return to the current location when finished
                dt.__color__ = hashcolor(this.__name__)
                if intType(value.__class__): value = float(value)
                if value.__class__ == float: dt.__silent__ = False; _bf_set_(dt, value, Format) # write
                elif value==None or value==u'': dt.__silent__ = False; __update__(dt) # read
                FILE._current._register_instance(dt)
            __update__=__update__ # specifically set for cf._set_update (may likely change) 
            if this.__dereferenced__: set=_bf_set_

        if hasattr( value, '__iter__' ):
            raise TypeError('iterable detected, please use array()()')
        return BF(value,Format)

define( 'bf8'           , bf(1)  )
define( 'bhalf bf16'    , bf(2)  ) # NOTE: don't confuse this with half-int aka short
define( 'bf24'          , bf(3)  )
define( 'bf32'          , bf(4)  )
define( 'bdouble bf64'  , bf(8)  )
define( 'bf128'         , bf(16) ) # also called a double-double