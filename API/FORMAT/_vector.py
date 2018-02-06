# -*- coding: utf-8 -*-
"""This module is the basis behind UGE's mechanics.
As of the 3.0.6 release, matrices have been deprecated in favor of vectors supporting everything up to quaternions, including colors.
Currently, transformation follows a general vec3 location, vec3 (euler) or quat rotation, vec3 scale, which uses less math than matrix transformation.
multi-channel vectors (implemented using properties) offer quick translations between vector spaces or math.
multi-dimensional vectors are a planned feature to possibly re-implement matrices for uses other than general transformation.
"""

# TODO: performance could use some work

from math import cos, sin, asin, atan2, sqrt
from ..OBJECT import UGEObject, newUGEObject, FloatProp
from ..utilities import stop
from ..CONST import define, UGE_CONSTANT, UGE_MODEL_SCRIPT

class UGE_VECTOR_FLAG(UGE_CONSTANT): pass

define( '''
        UGE_UNTRANSFORMED
        UGE_PRETRANSFORMED
        '''.split(), UGE_VECTOR_FLAG, [ UGE_MODEL_SCRIPT ])

def validate(vec,val,attr):
    if val==None: return
    val = getattr(val,'__value__',val) # from UGE data-type (bf32 or such)
    vtype = val.__class__
    if vtype is str: setattr(vec,attr,float(val))
    if numtype(vtype): setattr(vec,attr,val)
    # Anything unsupported 

order='XYZW'
class vector(UGEObject):
    """represents a (up to 4D) vector, quaternion, or color object"""
    __slots__ = order
    __disabled__ = {'Name'}
    
    __hash__ = lambda vec: hash(tuple(stop() if v is None else v for v in (vec.X,vec.Y,vec.Z,vec.W)))
    __repr__ = lambda vec: '<vector %s >'%(', '.join('%s: %s'%(attr,vec.__getattribute__(attr)) for attr in order))
    __eq__=lambda vec,other: (vec.X,vec.Y,vec.Z,vec.W)[:len(other)]==other[:len(other)] or vec.proxy is other or vec is other
    __ne__=lambda vec,other: (vec.X,vec.Y,vec.Z,vec.W)[:len(other)]!=other[:len(other)] and vec.proxy is not other and vec is not other
    __len__ = lambda vec: (vec.X!=None)+(vec.Y!=None)+(vec.Z!=None)+(vec.W!=None)
    
    def __new__(cls, *other: tuple, **kw ):
        vec=newUGEObject(cls,*other)
        vec.X = vec.Y = vec.Z = vec.W = None
        return vec
    
    #def new(vec,):
    
    def __setitem__(vec, item, val ):
        val = getattr(val,'__value__',val)
        itemType = item.__class__
        if itemType is slice: item = order[item]; itemType=str
        if itemType is str:
            item = item.lower()
            ilen = len(item)
            single = ilen==1
            if hasattr(val,'__iter__'):
                vlen = len(val)
                val = val[:ilen if vlen>ilen else vlen]
                if single: validate(vec,val[0],item); return
                if vlen<ilen: item=item[:vlen]; ilen = vlen
                
            if single: validate(vec,val,item)
            else:
                for k,v in zip(item,val): validate(vec,v,k)
            return
        elif itemType is int: validate(vec,val,order[item]); return
    
    def __getitem__(vec, item):
        itemType = item.__class__
        if itemType is slice: item = order[item]; itemType=str
        if itemType is str: return tuple(getattr(vec,a) for a in item.lower())
        elif itemType is int: return getattr(vec,order[item].lower())

FloatProp(vector,'X')
FloatProp(vector,'Y')
FloatProp(vector,'Z')
FloatProp(vector,'W')

'''
def _validate(v): # DEPRECATED
    if v==None: return
    if hasattr(v,'__value__'): v = v.__value__ # from UGE data-type (bf32 or such)
    vtype = v.__class__
    if vtype is str: return float(v) if '.' in v else int(v)
    if vtype is float or vtype is int: return v
    # Anything unsupported 

class vectorProxy(object): # secure frontend access
    __slots__ = list("XYZW")+['__iter__','__repr__','__len__','__getitem__','__eq__','__ne__']

_None4 = [None,None,None,None]
# noinspection PyPropertyDefinition
class vector(object):
    """efficient, general-purpose vector class"""
    __slots__ = ['_X','_Y','_Z','_W','next','__repr__','__getitem__','PT','transform','proxy']
    # NOTE: PT is a bool marking that this vector is in world space (T-Pose) rather than local space (GPU-data)
    
    X = property(lambda this: this._X, lambda this,value: this.__setattr__('_X',_validate(value)))
    Y = property(lambda this: this._Y, lambda this,value: this.__setattr__('_Y',_validate(value)))
    Z = property(lambda this: this._Z, lambda this,value: this.__setattr__('_Z',_validate(value)))
    W = property(lambda this: this._W, lambda this,value: this.__setattr__('_W',_validate(value)))
    def __init__(this,X=None,Y=None,Z=None,W=None):
        """represents a (up to 4D) vector, quaternion, or color object:
        vertices: X,Y,Z,W # quaternions included
         normals: I,J,K,H # bi-(normal/tangent) and tangent vectors included
             UVs: S,T,R,Q
          colors: R,G,B,A
        
        usage:
        V = vector([ 1., 1., 1. ])
        Q = vector(0,0,0,1, quat=True)
        E = Q.euler
        
        """
        mapping="XYZW"
        # from UGE data-type (array or struct)
        if hasattr(X,'__value__'): X = X.__value__
        if hasattr(Y,'__value__'): Y = Y.__value__
        if hasattr(Z,'__value__'): Z = Z.__value__
        if hasattr(W,'__value__'): W = W.__value__
        
        if hasattr(X,'__iter__'):
            xl = len(X)
            if xl<4: X[xl:]=_None4[xl:]
            X,Y,Z,W = X[:4]
        this.X, this.Y, this.Z, this.W = X,Y,Z,W
        
        # NOTE: for rotation quaternions, if W is 0, it's considered Euler
        # NOTE: quats are only used for rotation, where vec4s are only used for (X-scaled?) location
        
        _get = vector.__dict__.__getitem__
        # noinspection PyGlobalUndefined
        global __idx__; __idx__ = 0
        def _next():
            global __idx__
            try:
                value = _get(mapping[__idx__]).__get__(this)
                __idx__+=1
                if value==None: __idx__ = 0; raise StopIteration
                return value
            except IndexError: __idx__ = 0; raise StopIteration
        this.next = _next
        
        def _getitem(item):
            item_class = item.__class__
            if item_class==slice: return [_get(attr).__get__(this) for attr in mapping[item]]
            elif item_class==int: return _get(mapping[item]).__get__(this)
            elif item_class==str: return _get(item).__get__(this)
            else:
                raise TypeError('vector[item] expects int, slice, or str, not %s'%item.__class__.__name__)
        this.__getitem__ = _getitem
    
        this.__repr__ = lambda: '<vector %s >'%(', '.join('%s: %s'%(attr,_get(attr).__get__(this)) for attr in mapping)) # TODO: this could be built better
        
        proxy = this.proxy = vectorProxy()
        proxy.__iter__ = this.__iter__
        proxy.__repr__ = this.__repr__
        proxy.__len__ = this.__len__
        proxy.__getitem__ = _getitem
        proxy.__eq__ = this.__eq__
        proxy.__ne__ = this.__ne__
    
    __len__ = lambda this: (this.X!=None)+(this.Y!=None)+(this.Z!=None)+(this.W!=None)
    __iter__ = lambda this: this
    __eq__ = lambda this,other: tuple(this)==tuple(other)
    __ne__ = lambda this,other: tuple(this)!=tuple(other)
    
    @property
    def quat(this): # quat = this.quat
        """converts a Euler rotation vector to a quaternion (returns a copy if the vector already is a quaternion)"""
        # Tcll - credit to Eferno for this src
        if this.W!=None: return vector(this.X,this.Y,this.Z,this.W) # copy
        x,y,z=this.X,this.Y,this.Z
        t0 = cos(y*.5); t1 = sin(y*.5) # yaw
        t2 = cos(z*.5); t3 = sin(z*.5) # roll
        t4 = cos(x*.5); t5 = sin(x*.5) # pitch
        return vector(
            t0 * t3 * t4 - t1 * t2 * t5,
            t0 * t2 * t5 + t1 * t3 * t4,
            t1 * t2 * t4 - t0 * t3 * t5,
            t0 * t2 * t4 + t1 * t3 * t5 )
    
    @quat.setter
    def quat(this,quat): # this.quat = quat
        """Applies the result as a Euler rotation vector"""
        # Tcll - credit to Eferno for this src
        x,y,z,w=quat
        
        y2 = y*y
        t0 = -2. * ( y2 + z*z) + 1.
        t1 = +2. * (x*y - w*z)
        t2 = -2. * (x*z + w*y)
        t3 = +2. * (y*z - w*x)
        t4 = -2. * (x*x + y2 ) + 1.
    
        t2 =  1. if t2> 1. else t2
        t2 = -1. if t2<-1. else t2
        
        this.X = asin(t2)        # pitch
        this.Y = atan2(t1, t0)   # yaw
        this.Z = atan2(t3, t4)   # roll (Z is towards you)
        this.W = None
        
    @property
    def euler(this):
        """Ensures the result is a Euler rotation vector (returns a copy if the vector already is a euler)"""
        # Tcll - credit to Eferno for this src (same as above)
        x,y,z,w=this.X,this.Y,this.Z,this.W
        if not w: return vector(x,y,z)
        
        y2 = y*y
        t0 = -2. * ( y2 + z*z) + 1.
        t1 = +2. * (x*y - w*z)
        t2 = -2. * (x*z + w*y)
        t3 = +2. * (y*z - w*x)
        t4 = -2. * (x*x + y2 ) + 1.
    
        t2 =  1. if t2> 1. else t2
        t2 = -1. if t2<-1. else t2
        
        return vector(
            asin(t2),        # pitch
            atan2(t1, t0),   # yaw
            atan2(t3, t4))   # roll (Z is towards you)
        
    def normalize(this,quat=False,n3=False):
        """Returns a normalized vector.
        
        arguments:
        - (bool) quat: perform quaternion normalization (missing values will substitute 0)
        - (bool) n3: ignore the W coord (no effect if W is None)"""
        x,y,z,w=this.X,this.Y,this.Z,this.W
        if quat:
            if y==None: y=0
            if z==None: z=0
            if w==None: w=0
            d=1./sqrt( x*x + y*y + z*z + w*w )
            return vector( x*d , y*d , z*d , w*d )
        else:
            hasY,hasZ,hasW = y!=None,z!=None,w!=None
            d = 1./sqrt( x*x + (y*y if hasY else 0) + (z*z if hasZ else 0) + (w*w if hasW and not n3 else 0))
            return vector( x/d, y/d if hasY else None, z/d if hasZ else None, w/d if hasW and not n3 else w )
    
    @property
    def inverseQuat(this):
        """Gives an inversed quaternion vector. (expects a quaternion)"""
        # Tcll - credit to Matt Sitton for lending me his src.
        x,y,z,w=this.X,this.Y,this.Z,this.W
        if y==None: y=0
        if z==None: z=0
        if w==None: w=0
        len2 = x*x + y*y + z*z + w*w
        return vector( x/len2, y/len2, z/len2, w/len2 )
    
    def dot(this,other=None,d3=False):
        """Returns a dot product.
        
        arguments:
        - (vector/None) other: dot the given or this vector (missing values will substitute 0)
        - (bool) d3: ignore the W coord (no effect if W is None)"""
        if not other: other = this
        y,z,w,oy,oz,ow = this.Y,this.Z,this.W,other.Y,other.Z,other.W
        return this.X*other.X +\
               (y if y!=None else 0) * (oy if oy!=None else 0) +\
               (z if z!=None else 0) * (oz if oz!=None else 0) +\
               (((w if w!=None else 0) * (ow if ow!=None else 0)) if d3 else 0)
    
    mag = lambda this: sqrt(this.dot())
    
    def rotate(this, rvec, isquat=False):
        """Returns a rotated vector.
        
        arguments:
        - (bool) isquat: are we rotating a quaternion instead of a vec4?"""
        if rvec.W==None: rvec = rvec.quat # convert Euler to quat
        x,y,z,w=this.X,this.Y,this.Z,this.W
        rx,ry,rz,rw=rvec.X,rvec.Y,rvec.Z,rvec.W
        hasY,hasZ,hasW = y!=None,z!=None,w!=None
        if isquat:
            return vector( # Tcll - credit to Matt Sitton for lending me his src.
                w*rx + x*rw + y*rz - z*ry,
                w*ry + y*rw + z*rx - x*rz,
                w*rz + z*rw + x*ry - y*rx,
                w*rw - x*rx - y*ry - z*rz )
        else: # vec# (result should be transformed by the quat while maintaining it's dimensions)
            # Tcll - credit to Matt Sitton for lending me his src.
            if not hasY: y = 0.
            if not hasZ: z = 0.
            # multiply vector:
            vx =  rw*x + ry*z - rz*y
            vy =  rw*y + rz*x - rx*z
            vz =  rw*z + rx*y - ry*x
            vw = -rx*x - ry*y - rz*z
            # multply quat conjugate
            cx,cy,cz = -rvec.X, -rvec.Y, -rvec.Z # not using the conjugate property for performance
            return vector(  vw*cx + vx*rw + vy*cz - vz*cy,
                            vw*cy + vy*rw + vz*cx - vx*cz if hasY else None,
                            vw*cz + vz*rw + vx*cy - vy*cx if hasZ else None
                            # TODO: not sure what to do with vec4
            )
    
    def transform(this,ILoc,IRot,ISca):
        """Returns a vector transformed by the influence.
        
        arguments:
        - (bool) Bone: the bone to transform this vector by the given Bone"""

    conjugate = property( lambda this: vector(-this.X, -this.Y if this.Y else None, -this.Z if this.Z else None, this.W) )
    
    # operators:
    
    def __neg__(this):
        """Returns a negative vector"""
        x,y,z,w=this.X,this.Y,this.Z,this.W
        return vector( -x,-y if y!=None else None,-z if z!=None else None )
    inverse = property(__neg__)
    @inverse.setter
    def inverse(this,inv):
        """Applies the result as a positive vector. (from a negative vector)"""
        if inv.__class__!=vector: inv = -vector(inv) # safety first
        this.X,this.Y,this.Z,this.W = inv.X,inv.Y,inv.Z,inv.W # doing this because a W of None returns 3 values
    
    def __mul__(this,other): # this*other
        x,y,z,w=this.X,this.Y,this.Z,this.W
        OC = other.__class__
        if numtype(OC):
            return vector( x*other,
                y*other if y!=None else None,
                z*other if z!=None else None,
                w*other if w!=None else None)
        elif not OC==vector: other=vector(other)
        ox,oy,oz,ow = other.X,other.Y,other.Z,other.W
        return vector( x*ox,
            (y if y!=None else 1) * oy if oy!=None else None,
            (z if z!=None else 1) * oz if oz!=None else None,
            (w if w!=None else 1) * ow if ow!=None else None
        )
        
    def __div__(this,other): # this/other
        x,y,z,w=this.X,this.Y,this.Z,this.W
        OC = other.__class__
        if numtype(OC):
            return vector( x/other,
                y/other if y!=None else None,
                z/other if z!=None else None,
                w/other if w!=None else None)
        elif not OC==vector: other=vector(other)
        ox,oy,oz,ow = other.X,other.Y,other.Z,other.W
        return vector( x/ox,
            (y if y!=None else 1) / oy if oy!=None else None,
            (z if z!=None else 1) / oz if oz!=None else None,
            (w if w!=None else 1) / ow if ow!=None else None
        )
    
    def __add__(this,other): # this+other
        x,y,z,w=this.X,this.Y,this.Z,this.W
        OC = other.__class__
        if numtype(OC):
            return vector( x+other,
                y+other if y!=None else None,
                z+other if z!=None else None,
                w+other if w!=None else None)
        elif not OC==vector: other=vector(other)
        ox,oy,oz,ow = other.X,other.Y,other.Z,other.W
        return vector( x+ox,
            (y if y!=None else 1) + oy if oy!=None else None,
            (z if z!=None else 1) + oz if oz!=None else None,
            (w if w!=None else 1) + ow if ow!=None else None
        )
        
    def __sub__(this,other): # this-other
        x,y,z,w=this.X,this.Y,this.Z,this.W
        OC = other.__class__
        if numtype(OC):
            return vector( x-other,
                y-other if y!=None else None,
                z-other if z!=None else None,
                w-other if w!=None else None)
        elif not OC==vector: other=vector(other)
        ox,oy,oz,ow = other.X,other.Y,other.Z,other.W
        return vector( x-ox,
            (y if y!=None else 1) - oy if oy!=None else None,
            (z if z!=None else 1) - oz if oz!=None else None,
            (w if w!=None else 1) - ow if ow!=None else None
        )'''


def VectorProp( cls: object, attr: str ):
    """reassigns a vector verification property to an existing member_descriptor attribute"""
    initializers = properties[cls] = properties.get(cls,set())
    dsc = cls.__dict__[attr]
    dscget = dsc.__get__; dscset = dsc.__set__
    def setter(obj, val): dscget(obj,cls)[:] = val
    property( dscget, setter )
    initializers.add( lambda obj: dscset(obj,vector(obj,0)) )