# -*- coding: utf-8 -*-
"""UGE Primitive classes and associate functions"""

# noinspection PyShadowingNames,PyProtectedMember
def private():
    """private namespace"""
    
    from . import Object
    from ..OBJECT import UGEObject, newUGEObject, extension, UGECollection, CollectionProp, UGEChannels, ChannelsProp, StringProp, FloatProp, _protected, properties
    
    # NOTE: these property types might eventually be renamed and globalized after some work.

    def singleProp( cls: object, attr: str, iattr: str ):
        """single value/index"""
        name = cls.__name__; initializers = properties[name] = properties.get(name,set())
        dsc = cls.__dict__[attr]; idsc = cls.__dict__[iattr]
        dscget = dsc.__get__; dscset = dsc.__set__; idscget = idsc.__get__; idscset = idsc.__set__
        def getter(Fp) -> UGEVector: """get vector"""; idx = idscget(Fp ); return None if idx is None else dscget(Fp )(idx )
        def setter(obj, val: iterable ):
            """set vector"""
            if val is None: idscset(obj,val)
            else:
                if idscget(obj) is None: idscset( obj, dscget(obj).new(val).Index )
                else: dscget(obj)[idscget(obj)] = val
        setattr(cls,attr,property( getter, setter ))
        def isetter(obj, val: (int, None)):
            """set index"""
            val = getattr(val,'__value__',val)
            if val.__class__ in {str,int,float}: val = int(val)
            elif val is not None: print('ERROR: %s.%s received an invalid value (%s)'%(name,attr,val))
            idscset(obj,val)
        setattr(cls,iattr,property( idscget, isetter ))
        def init(obj: UGEObject): """initializer"""; dscset( obj, getattr(obj.__parents__['Object'],'%ss'%attr) ); idscset( obj, None )
        initializers.add( init )

    forwarder_relations = (UGEChannels or UGECollection,function) # TODO: can't have this var if we're going to globalize
    def multiprop( cls: object, attr: str, iattr: str ):
        """multi value/index"""
        name = cls.__name__; initializers = properties[name] = properties.get(name,set())
        dsc = cls.__dict__[attr]; idsc = cls.__dict__[iattr]
        dscget = dsc.__get__; dscset = dsc.__set__; idscget = idsc.__get__; idscset = idsc.__set__
        def setter(Fp, val: iterable): """Fp.UVs = val"""; dscget(Fp)[:] = val
        def isetter(Fp, val: iterable): """Fp.UVIndices = val"""; idscget(Fp)[:] = val
        setattr(cls,attr,property( dscget, setter ))
        setattr(cls,iattr,property( idscget, isetter ))
        def init(obj: UGEObject):
            """initializer"""
            global forwarder_relations # Tcll - don't ask how this is linking without the global in multiprop, idek myself.
            forwarder_relations = (getattr(obj.__parents__['Object'],attr),   idscget)
            dscset( obj, Forwarder(obj) ); idscset( obj, {} )
        initializers.add( init )
    
    class Forwarder(UGEObject):
        """unofficial, multipriop forwarder"""
        __disabled__ = {'Name','Index'}
        def __new__(cls, *other: tuple ):
            Fw = newUGEObject(cls, *other); Fp = Fw.__parents__['Facepoint']
            array, getindices = forwarder_relations
            arraygetitem = array.__getitem__; arraycall = array.__call__
            if array.__class__ is UGEChannels:
                def getitem( item ) -> object:
                    """Fp.UVs[item]"""
                    idx = getindices(Fp).get(item,None)
                    return None if idx is None else arraycall(item)(idx)
                Fw.__getitem__ = getitem
                def setitem( item, val: object ):
                    """Fp.UVs[item] = val"""
                    getindices(Fp)[item] = arraygetitem(item).Index(val)
                Fw.__setitem__ = setitem
                Fw.__iter__ = lambda: ( (c, arraycall(c)(i)) for c,i in getindices(Fp).items() )
                def contains(item) -> bool:
                    """item in Fp.UVs"""
                    for ch,idx in getindices(Fp).items():
                        if arraycall(ch)(idx) == item: return True
                    return False
                Fw.__contains__ = contains
            else:
                def getitem( item ) -> object:
                    """Fp.(Weights,Materials)[item]"""
                    idx = getindices(Fp).get(item,None)
                    return None if idx is None else arraycall(idx)
                Fw.__getitem__ = getitem
                def setitem( item, val: object ):
                    """Fp.(Weights,Materials)[item] = val"""
                    getindices(Fp)[item] = array.Index(val)
                Fw.__setitem__ = setitem
                Fw.__iter__ = lambda: ( (k, arraycall(i)) for k,i in getindices(Fp).items() )
                # TODO: figure out how to reasonably support
                #def contains(item) -> bool:
                #    """item in Fp.(Weights,Materials)"""
                #    for k,idx in getindices(Fp).items():
                #        if arraycall(idx) == item: return True
                #    return False
                #Fw.__contains__ = contains
            return Fw

    class Facepoint(UGEObject):
        """UGE Facepoint"""
        __slots__ = [ 'Vertice',    'VerticeIndex',
                      'Normal',     'NormalIndex',
                      'BiNormal',   'BiNormalIndex',
                      'Tangent',    'TangentIndex',
                      'Colors',     'ColorIndices',
                      'UVs',        'UVIndices',
                      'Weights',    'WeightIndices',
                      'Materials',  'MaterialIndices']
        __disabled__ = {'Name'}
    
    singleProp( Facepoint, 'Vertice',   'VerticeIndex'    )
    singleProp( Facepoint, 'Normal',    'NormalIndex'     )
    singleProp( Facepoint, 'BiNormal',  'BiNormalIndex'   )
    singleProp( Facepoint, 'Tangent',   'TangentIndex'    )
    multiprop(  Facepoint, 'Colors',    'ColorIndices'    ) # { channel: index }
    multiprop(  Facepoint, 'UVs',       'UVIndices'       ) # { channel: index }
    multiprop(  Facepoint, 'Weights',   'WeightIndices'   ) # { Bone: Index }
    multiprop(  Facepoint, 'Materials', 'MaterialIndices' ) # { index: index }
    globals()['Facepoint'] = Facepoint

    # Facepoint.*Vector* >>> vector(0,0(,0(,1))) if not defined
    # Facepoint.*Vector* = (0,0,0,1)
    # if you change the index, the vector will change
    # if you change the vector, the index may change
    
    class Primitive(UGEObject):
        """UGE Primitive"""
        __slots__=['Type','FacepPoints']
        __disabled__ = {'Name'}
        
        def __new__( cls, *other: tuple, **kw ):
            Pr = newUGEObject(cls,*other)
            Pr.Type = None
            return Pr
        
        def new(cls, parents: mappingproxy, holder: UGECollection, item, *args, **kw):
            """Create a new primitive instance of the specified type"""
            Pr = cls.__new__(parents,holder,*args,**kw)
            if item.__class__ is dict
            Pr.Type = item
            return Pr

    CollectionProp( Primitive, 'Facepoints', Facepoint, __builtin__ = "CurrentFacepoint" )
    globals()['Primitive'] = Primitive

    class Weight(UGEObject):
        """UGE Weight"""
        __slots__ = ['Value']
        __disabled__ = {'Name'}
        def __new__(cls, *other: tuple ):
            Wt = newUGEObject(cls, *other)
            Wt.Value = 1.0
            return Wt
    FloatProp(Weight,'Value')
    globals()['Weight'] = Weight
    
    new = object.__new__
    class mesh(object):
        """mesh Type"""
        __slots__=['Name','Vertices','Normals','BiNormals','Tangents','Colors','UVs','Weights','Primitives','__owner__']
        def __new__(cls,Ob: UGEObject):
            Me = new(cls)
            Me.__owner__ = Ob
            Me.Name=Ob.Name
            for initializer in properties.get('mesh',set()): initializer(Me)
            return Me
        __eq__ = lambda this,other: this.Name == other or this is other
        __ne__ = lambda this,other: this.Name != other and this is not other
    StringProp(     mesh, 'Name'                  )
    CollectionProp( mesh, 'Vertices',   UGEVector )
    CollectionProp( mesh, 'Normals',    UGEVector )
    CollectionProp( mesh, 'BiNormals',  UGEVector ) # NOTE: some sources (such as the IQM demo) call these BiTangents
    CollectionProp( mesh, 'Tangents',   UGEVector )
    ChannelsProp(   mesh, 'Colors',     UGEVector )
    ChannelsProp(   mesh, 'UVs',        UGEVector )
    CollectionProp( mesh, 'Weights',    Weight    )
    ChannelsProp(   mesh, 'Primitives', Primitive, __builtin__ = 'CurrentPrimitive' )
    globals()['mesh'] = mesh

    getData, setData = _protected['Object']['Data']
    
    objectextension=extension('Object')
    @objectextension
    def Primitives(Ob: Object):
        """Object.Primitives"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).Primitives
        print('ERROR: Object.Primitives cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Primitives(Ob: Object, val: object):
        """Set Object.Primitives"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).Primitives[:] = val
    
    # lists
    @objectextension
    def Vertices(Ob: Object):
        """Object.Vertices"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).Vertices
        print('ERROR: Object.Vertices cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Vertices(Ob: Object, val: object):
        """Set Object.Vertices"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).Vertices[:] = val
        
    @objectextension
    def Normals(Ob: Object):
        """Object.Normals"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).Normals
        print('ERROR: Object.Normals cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Normals(Ob: Object, val: object):
        """Set Object.Normals"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).Normals[:] = val
        
    @objectextension
    def BiNormals(Ob: Object):
        """Object.BiNormals"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).BiNormals
        print('ERROR: Object.BiNormals cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def BiNormals(Ob: Object, val: object):
        """Set Object.BiNormals"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).BiNormals[:] = val
        
    @objectextension
    def Tangents(Ob: Object):
        """Object.Tangents"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).Tangents
        print('ERROR: Object.Tangents cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Tangents(Ob: Object, val: object):
        """Set Object.Tangents"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).Tangents[:] = val
        
    @objectextension
    def Colors(Ob: Object):
        """Object.Colors"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).Colors
        print('ERROR: Object.Colors cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Colors(Ob: Object, val: object):
        """Set Object.Colors"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).Colors[:] = val
        
    @objectextension
    def UVs(Ob: Object):
        """Object.UVs"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).UVs
        print('ERROR: Object.UVs cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def UVs(Ob: Object, val: object):
        """Set Object.UVs"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).UVs[:] = val

    @objectextension
    def Weights(Ob: Object):
        """Object.UVs"""
        if getData(Ob) is None: setData(Ob, mesh(Ob))
        if Ob.Type=='mesh': return getData(Ob).Weights
        print('ERROR: Object.Weights cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Weights(Ob: Object, val: object):
        """Set Object.UVs"""
        if getData(Ob) is None: setData(Ob,mesh(Ob))
        getData(Ob).Weights[:] = val
        
    return mesh, Weight, Primitive, Facepoint


mesh, Weight, Primitive, Facepoint = private()
del private

from . import Material, Bone, UGEVector

#from . import validObjectTypes
from .. import UGE_GLOBAL_WRAPPER, register
from ..CONST import define, UGE_CONSTANT, UGE_MODEL_SCRIPT, UGE_VECTOR_FLAG, UGE_PRETRANSFORMED, UGE_TRIANGLES

class UGE_PRIMITIVE_TYPE(UGE_CONSTANT ): """UGE Primitive Type"""
define( '''
        UGE_POINTS
        UGE_LINES UGE_LINESTRIP UGE_LINELOOP
        UGE_TRIANGLES UGE_TRIANGLESTRIP UGE_TRIANGLEFAN
        UGE_QUADS UGE_QUADSTRIP
        UGE_POLYGON
        '''.split(), UGE_PRIMITIVE_TYPE, [ UGE_MODEL_SCRIPT] )

# TODO: triangulate

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetVertices(Vertices: [UGEVector], flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED ):
    """Sets the vertice array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh':
            CurrentScope.UGE_VECTOR_FLAG = flag
            CurrentObject.Vertices = Vertices
        else: print('ERROR: ugeSetVertices() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetVertices() expected a defined Object.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetNormals(Normals: [UGEVector], flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED ):
    """Sets the normal array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh':
            CurrentScope.UGE_VECTOR_FLAG = flag
            CurrentObject.Normals = Normals
        else: print('ERROR: ugeSetNormals() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetNormals() expected a defined Object.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetBiNormals(BiNormals: [UGEVector], flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED ):
    """Sets the binormal/bitangent array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh':
            CurrentScope.UGE_VECTOR_FLAG = flag
            CurrentObject.BiNormals = BiNormals
        else: print('ERROR: ugeSetBiNormals() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBiNormals() expected a defined Object.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetTangents(Tangents: [UGEVector], flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED ):
    """Sets the tangent array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh':
            CurrentScope.UGE_VECTOR_FLAG = flag
            CurrentObject.Tangents = Tangents
        else: print('ERROR: ugeSetTangents() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetTangents() expected a defined Object.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetColors(Colors: [UGEVector], channel: int = 0 ):
    """Sets the color array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh': CurrentObject.Colors[channel] = Colors
        else: print('ERROR: ugeSetColors() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetColors() expected a defined Object.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetUVs(UVs: [UGEVector], channel: int = 0 ):
    """Sets the UV array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh': CurrentObject.UVs[channel] = UVs
        else: print('ERROR: ugeSetUVs() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetUVs() expected a defined Object.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetWeights(Weights: [float] ):
    """Sets the Weight array of the current mesh."""
    if CurrentObject:
        if CurrentObject.Type == 'mesh': CurrentObject.Weights = Weights
        else: print('ERROR: ugeSetWeights() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetWeights() expected a defined Object.')

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetPrimitive(Primitive: [UGE_PRIMITIVE_TYPE, Primitive, int] = UGE_TRIANGLES, mesh: str = None ) -> Primitive:
    """Creates or References a UGE Primitive"""
    if CurrentObject:
        if CurrentObject.Type == 'mesh': return CurrentObject.Primitives.new(Primitive,mesh)
        else: print('ERROR: ugeSetPrimitive() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetPrimitive() expected a defined Object.')

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFacepoint(Facepoint: [Facepoint, int] = None):
    """Creates or References a UGE Facepoint in the current primitive"""
    if CurrentPrimitive: return CurrentPrimitive.FacePoints.new(Facepoint)
    else: print('ERROR: ugeSetFacepoint() expected a defined Primitive.')
    
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpVerticeIndex(Index: int):
    """Sets the current Facepoint's vertice index"""
    if CurrentFacepoint: CurrentFacepoint.VerticeIndex = Index
    else: print('ERROR: ugeSetFpVerticeIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpNormalIndex(Index: int):
    """Sets the current Facepoint's normal index"""
    if CurrentFacepoint: CurrentFacepoint.NormalIndex = Index
    else: print('ERROR: ugeSetFpNormalIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpBiNormalIndex(Index: int):
    """Sets the current Facepoint's binormal index"""
    if CurrentFacepoint: CurrentFacepoint.BiNormalIndex = Index
    else: print('ERROR: ugeSetFpBiNormalIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpTangentIndex(Index: int):
    """Sets the current Facepoint's tangent index"""
    if CurrentFacepoint: CurrentFacepoint.TangentIndex = Index
    else: print('ERROR: ugeSetFpTangentIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpColorIndex(Index: int, channel: int = 0):
    """Sets the current Facepoint's color index"""
    if CurrentFacepoint: CurrentFacepoint.ColorIndices[channel] = Index
    else: print('ERROR: ugeSetFpColorIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpUVIndex(Index: int, channel: int = 0):
    """Sets the current Facepoint's UV index"""
    if CurrentFacepoint: CurrentFacepoint.UVIndices[channel] = Index
    else: print('ERROR: ugeSetFpColorIndex() expected a defined Facepoint.')

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpWeightIndex(Bone: (str, Bone), Index: int):
    """Sets the current Facepoint's Weight index"""
    if CurrentFacepoint: CurrentFacepoint.WeightIndices[Bone] = Index
    else: print('ERROR: ugeSetFpWeightIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpMaterialIndex(Index: int, MaterialIndex: int):
    """Sets the current Facepoint's Material index"""
    if CurrentFacepoint: CurrentFacepoint.MaterialIndices[Index] = MaterialIndex
    else: print('ERROR: ugeSetFpMaterialIndex() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpVertice(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None, flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED):
    """Sets the current Facepoint's vertice."""
    if CurrentFacepoint:
        CurrentFacepoint.Vertice = { 'XYZW':X, 'flag':flag } if iterable(X) else { 'X':X, 'Y':Y, 'Z':Z, 'W':W, 'flag':flag }
        return CurrentFacepoint.Vertice
    else: print('ERROR: ugeSetFpVertice() expected a defined Facepoint.')
    
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpNormal(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None, flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED):
    """Sets the current Facepoint's normal."""
    if CurrentFacepoint:
        CurrentFacepoint.Normal = { 'XYZW':X, 'flag':flag } if iterable(X) else { 'X':X, 'Y':Y, 'Z':Z, 'W':W, 'flag':flag }
        return CurrentFacepoint.Normal
    else: print('ERROR: ugeSetFpNormal() expected a defined Facepoint.')
    
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpBiNormal(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None, flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED):
    """Sets the current Facepoint's binormal."""
    if CurrentFacepoint:
        CurrentFacepoint.BiNormal = { 'XYZW':X, 'flag':flag } if iterable(X) else { 'X':X, 'Y':Y, 'Z':Z, 'W':W, 'flag':flag }
        return CurrentFacepoint.BiNormal
    else: print('ERROR: ugeSetFpBiNormal() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpTangent(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None, flag: UGE_VECTOR_FLAG = UGE_PRETRANSFORMED):
    """Sets the current Facepoint's tangent."""
    if CurrentFacepoint:
        CurrentFacepoint.Tangent = { 'XYZW':X, 'flag':flag } if iterable(X) else { 'X':X, 'Y':Y, 'Z':Z, 'W':W, 'flag':flag }
        return CurrentFacepoint.Tangent
    else: print('ERROR: ugeSetFpTangent() expected a defined Facepoint.')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpColor(R: (float, int, str, tuple, list), G: (float, int, str) = None, B: (float, int, str) = None, A: (float, int, str) = None, channel: int = 0):
    """Sets the current Facepoint's color."""
    if CurrentFacepoint:
        CurrentFacepoint.Colors[channel] = R if iterable(R) else (R,G,B,A)
        return CurrentFacepoint.Colors[channel]
    else: print('ERROR: ugeSetFpColor() expected a defined Facepoint.')
    
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpUV(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None, channel: int = 0):
    """Sets the current Facepoint's UV."""
    if CurrentFacepoint:
        CurrentFacepoint.UVs[channel] = X if iterable(X) else (X,Y,Z,W)
        return CurrentFacepoint.UVs[channel]
    else: print('ERROR: ugeSetFpUV() expected a defined Facepoint.')

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpWeight(Bone: (str, Bone), Value: float = 1.0):
    """Sets a weight on the current Facepoint."""
    if CurrentFacepoint:
        CurrentFacepoint.Weights[Bone] = Value
        return CurrentFacepoint.WeightIndices[Bone]
    else: print('ERROR: ugeSetFpWeight() expected a defined Facepoint.')

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetFpMaterial(Index: int, Material: (str, Material)):
    """Sets the current Facepoint's UV."""
    if CurrentFacepoint:
        CurrentFacepoint.Materials[Index] = Material
        return CurrentFacepoint.Materials[Index]
    else: print('ERROR: ugeSetFpMaterial() expected a defined Facepoint.')
