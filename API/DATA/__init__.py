# -*- coding: utf8 -*-
from sys import modules
from .. import CONST

UGE_GLOBAL_WRAPPER=modules['/UGE_GLOBAL_WRAPPER/'] # moddable API wrapper
register=modules['/register/'] # function registration

# noinspection PyUnusedLocal
def readonly(dt,*args,**kwargs):
    raise ValueError("'%s' objects are not writable"%dt.__name__)

# noinspection PyUnresolvedReferences,PyUnusedLocal
class UGE_DATATYPE(object): # Tcll - temporary magic-method container, used until more port-work can be done.
    __slots__=[]
    '''
    def __lt__(dt, o): return dt.__value__<o
    def __le__(dt, o): return dt.__value__<=o
    def __eq__(dt, o): return dt.__value__==o
    def __ne__(dt, o): return dt.__value__!=o
    def __gt__(dt, o): return dt.__value__>o
    def __ge__(dt, o): return dt.__value__>=o

    def __cmp__(dt,o): return cmp(dt.__value__,o)
    def __hash__(dt): return hash(dt.__value__)

    def __nonzero__(dt): return bool(dt.__value__)
    def __unicode__(dt): return unicode(dt.__value__)

    def __add__(dt, o): return dt.__value__+o
    def __sub__(dt, o): return dt.__value__-o
    def __mul__(dt, o): return dt.__value__*o
    def __div__(dt, o): return dt.__value__/o
    def __truediv__(dt, o): return dt.__value__/o
    def __floordiv__(dt, o): return dt.__value__//o
    def __mod__(dt, o): return dt.__value__%o
    #def __divmod__(dt, o):
    def __pow__(dt, o): return dt.__value__**o
    def __lshift__(dt, o): return dt.__value__<<o
    def __rshift__(dt, o): return dt.__value__>>o
    def __and__(dt, o): return dt.__value__&o
    def __xor__(dt, o): return dt.__value__^o
    def __or__(dt, o): return dt.__value__|o

    def __radd__(dt, o): return o+dt.__value__
    def __rsub__(dt, o): return o-dt.__value__
    def __rmul__(dt, o): return o*dt.__value__
    def __rdiv__(dt, o): return o/dt.__value__
    def __rtruediv__(dt, o): return o/dt.__value__
    def __rfloordiv__(dt, o): return o//dt.__value__
    def __rmod__(dt, o): return o%dt.__value__
    #def __rdivmod__(dt, o):
    def __rpow__(dt, o): return o**dt.__value__
    def __rlshift__(dt, o): return o<<dt.__value__
    def __rrshift__(dt, o): return o<<dt.__value__
    def __rand__(dt, o): return o&dt.__value__
    def __rxor__(dt, o): return o^dt.__value__
    def __ror__(dt, o): return o|dt.__value__
    # NOTE: ^ unlike most implementations, these do not take extra CPU steps to do the same job.

    # Tcll - future implementations may allow updating the file data with these methods
    def __iadd__(dt, o): readonly(dt)
    def __isub__(dt, o): readonly(dt)
    def __imul__(dt, o): readonly(dt)
    def __idiv__(dt, o): readonly(dt)
    def __itruediv__(dt, o): readonly(dt)
    def __ifloordiv__(dt, o): readonly(dt)
    def __imod__(dt, o): readonly(dt)
    def __ipow__(dt, o, m=None): readonly(dt)
    def __ilshift__(dt, o): readonly(dt)
    def __irshift__(dt, o): readonly(dt)
    def __iand__(dt, o): readonly(dt)
    def __ixor__(dt, o): readonly(dt)
    def __ior__(dt, o): readonly(dt)

    def __neg__(dt): return -dt.__value__
    def __pos__(dt): return +dt.__value__
    def __abs__(dt): return abs(dt.__value__)
    def __invert__(dt): return ~dt.__value__

    def __int__(dt): return int(dt.__value__)
    def __long__(dt): return long(dt.__value__)
    def __float__(dt): return float(dt.__value__)
    def __complex__(dt): return complex(dt.__value__)

    def __oct__(dt): return oct(dt.__value__)
    def __hex__(dt): return hex(dt.__value__)

    def __str__(dt): return str(dt.__value__)
    def __repr__(dt): return repr(dt.__value__)
    '''

    __cmp__ =       lambda dt,o: dt.__value__.__cmp__(o)
    __lt__ =        lambda dt, o: dt.__value__ < o
    __le__ =        lambda dt, o: dt.__value__ <= o
    __eq__ =        lambda dt, o: dt.__value__ == o
    __ne__ =        lambda dt, o: dt.__value__ != o
    __gt__ =        lambda dt, o: dt.__value__ > o
    __ge__ =        lambda dt, o: dt.__value__ >= o
    __hash__ =      lambda dt: dt.__value__.__hash__()
    __nonzero__ =   lambda dt: dt.__value__.__nonzero__()
    __index__ =     lambda dt: dt.__value__.__index__()
    __add__ =       lambda dt,o: dt.__value__ + o
    __sub__ =       lambda dt,o: dt.__value__ - o
    __mul__ =       lambda dt,o: dt.__value__ * o
    __div__ =       lambda dt,o: dt.__value__ / o
    __truediv__ =   lambda dt,o: dt.__value__ / o
    __floordiv__ =  lambda dt,o: dt.__value__ // o
    __mod__ =       lambda dt,o: dt.__value__ % o
    __pow__ =       lambda dt,o: dt.__value__ ** o
    __lshift__ =    lambda dt,o: dt.__value__ << o
    __rshift__ =    lambda dt,o: dt.__value__ >> o
    __and__ =       lambda dt,o: dt.__value__ & o
    __xor__ =       lambda dt,o: dt.__value__ ^ o
    __or__ =        lambda dt,o: dt.__value__ | o
    __radd__ =      lambda dt,o: o + dt.__value__
    __rsub__ =      lambda dt,o: o - dt.__value__
    __rmul__ =      lambda dt,o: o * dt.__value__
    __rdiv__ =      lambda dt,o: o / dt.__value__
    __rtruediv__ =  lambda dt,o: o / dt.__value__
    __rfloordiv__ = lambda dt,o: o // dt.__value__
    __rmod__ =      lambda dt,o: o % dt.__value__
    __rpow__ =      lambda dt,o: o ** dt.__value__
    __rlshift__ =   lambda dt,o: o << dt.__value__
    __rrshift__ =   lambda dt,o: o >> dt.__value__
    __rand__ =      lambda dt,o: o & dt.__value__
    __rxor__ =      lambda dt,o: o ^ dt.__value__
    __ror__ =       lambda dt,o: o | dt.__value__
    __neg__ =       lambda dt: -dt.__value__
    __pos__ =       lambda dt: +dt.__value__
    __abs__ =       lambda dt: dt.__value__.__abs__()
    __invert__ =    lambda dt: dt.__value__.__invert__()
    __int__ =       lambda dt: dt.__value__.__int__()
    __long__ =      lambda dt: dt.__value__.__long__()
    __float__ =     lambda dt: dt.__value__.__float__()
    __oct__ =       lambda dt: dt.__value__.__oct__()
    __hex__ =       lambda dt: dt.__value__.__hex__()
    __str__ =       lambda dt: dt.__value__.__str__()
    __repr__ =      lambda dt: dt.__value__.__repr__()
    
    __iadd__=__isub__=__imul__=__idiv__=__itruediv__=__ifloordiv__=__imod__=__ipow__=\
    __ilshift__=__irshift__=__iand__=__ixor__=__ior__=readonly
    
    #def __coerce__(dt, o):
    '''
    def __setattr__(dt,n,v):
        if n=='__value__':
            raise ValueError("attribute '__value__' of '%s' objects is not writable"%dt.__name__)
        dt.__dict__[n]=v
    '''

def define(names,Type): # registers extended names for datatype objects
    for name in names.split():
        [C.NS.update({name:Type}) for C in CONST.__dict__.values() if C.__class__.__name__=='UGE_Scope_Type'] # future-safe

# register extensible data designers and structs:
from . import u,s,f,h,string,array,struct

###########################################################################################
# data transformation functions
###########################################################################################

#TODO:
# Field( [1,7,15]        ,bu8)() # read
# Field( ['1','3','4']   ,bu8)([1,7,15]) # write

@UGE_GLOBAL_WRAPPER
@register(all,False)
def field(Template,value):
    """turns an unsigned bit-field into multiple values.
    
    usage:
    - Field( [1,7,15]        ,255) # int representation (bit mask)
    - Field( ['1','3','4']   ,255) # bit representation (number of bits)
    returns: [1,7,15]
    
    - Field(['1','3','4'],[1,7,15])
    returns: 255
    """
    if hasattr(value,'__value__'): value=value.__value__
    #if Template==[]: template=[len(bin(value))]
    if value.__class__ is int: #return list
        if value<0:
            raise ValueError("int values must be unsigned")
        else:
            sums = [int(v) if v.__class__==str else len(bin(v))-2 for v in Template]
            return [(value>> (sum(sums[:i]) if i>0 else 0) )&(~(~0<<int(t)) if t.__class__ is str else t) for i,t in enumerate(Template)]
    if value.__class__ is list: #return int
        if len(Template)==len(value): #value-list must equal the template
            res = 0
            for t, v in zip(Template, value)[::-1]: res = (res << (int(t) if t.__class__ is str else t.bit_length()) )|v
            return res
        else:
            raise ValueError("Template length must match value length")
    else:
        raise ValueError("`value` must be a list or unsigned int")

del register
