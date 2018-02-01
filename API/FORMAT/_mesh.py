# -*- coding: utf-8 -*-
"""UGE Primitive classes and associate functions"""

from . import vector
#from . import validObjectTypes, VectorProp
from .. import CONST, UGE_GLOBAL_WRAPPER, register
from ..OBJECT import UGEObject, extension, UGECollection, CollectionProp, UGEChannels#, ChannelsProp, IntProp

CONST.define( '''
        UGE_UNTRANSFORMED
        UGE_PRETRANSFORMED
        '''.split(), type('UGE_Vector_Flag', (CONST.UGE_CONSTANT,), {}), [ CONST.UGE_MODEL_SCRIPT ])
CONST.define( '''
        UGE_POINTS
        UGE_LINES UGE_LINESTRIP UGE_LINELOOP
        UGE_TRIANGLES UGE_TRIANGLESTRIP UGE_TRIANGLEFAN
        UGE_QUADS UGE_QUADSTRIP
        UGE_POLYGON
        '''.split(), type('UGE_Primitive', (CONST.UGE_CONSTANT,), {}), [ CONST.UGE_MODEL_SCRIPT ])
# TODO: ^.triangulate()

# noinspection PyUnresolvedReferences
def private() -> None:
    """anything done here is not passed throughout FORMAT"""

    forwarder_relations = (UGEChannels or UGECollection,function) # array, getindices
    
    class Forwarder(UGEObject):
        """unofficial"""

        # noinspection PyUnresolvedReferences
        def __new__(cls, *other: tuple ):
            array, getindices = forwarder_relations
            Fw = UGEObject.__new__(cls, *other)
            Fp = Fw.__parent__
            arrayget = array.__getitem__
            if array.__class__ is UGEChannels: Fw.__getitem__ = lambda item: arrayget( (getindices(Fp)[item], item) )
            else: Fw.__getitem__ = lambda item: arrayget( getindices(Fp)[item] )
            return Fw
    
    class Facepoint(UGEObject):
        """UGE Facepoint"""
        __public__ = {  'Vertice':{'p','w'},    'VerticeIndex': {'w'},
                        'Normal':{'p','w'},     'NormalIndex': {'w'},
                        'BiNormal':{'p','w'},   'BiNormalIndex': {'w'},
                        'Tangent':{'p','w'},    'TangentIndex': {'w'},
                        'Colors':{'p','w'},     'ColorIndices': {'w'},
                        'UVs':{'p','w'},        'UVsIndex': {'w'},
                        'Weights':{'p','w'},    'WeightIndices': {'w'},
                        'Materials':{'p','w'},  'MaterialIndices': {'w'}}
        __disabled__ = {'Name'}
        def __new__(cls, *other: tuple ):
            global forwarder_relations
            Fp = UGEObject.__new__(cls, *other)
            Ob = Fp.__parent__.__parent__
            # assign collections to instances
            Vset( Fp, Ob.Vertices );    VIset( Fp, None )
            Nset( Fp, Ob.Normals );     NIset( Fp, None )
            Bset( Fp, Ob.BiNormals );   BIset( Fp, None )
            Tset( Fp, Ob.Tangents );    TIset( Fp, None )

            forwarder_relations = (Ob.Colors,   CIget)
            Cset( Fp, Forwarder(Fp) );       CIset( Fp, {} ) # { channel, index }
            
            forwarder_relations = (Ob.UVs,      UIget)
            Uset( Fp, Forwarder(Fp) );          UIset( Fp, {} ) # { channel, index }
            
            forwarder_relations = (Ob.Weights,  WIget)
            Wset( Fp, Forwarder(Fp) );      WIset( Fp, {} ) # { 'BoneName', Index }
            
            forwarder_relations = (Ob.Materials,MIget)
            Mset( Fp, Forwarder(Fp) );    MIset( Fp, [] ) # [ 'MaterialName' ]
            return Fp
    globals()['Facepoint'] = Facepoint
    
    def singleProp( cls, attr, iattr ) -> ( function, function ):
        """single value/index"""
        name = Facepoint.__name__
        dsc = cls.__dict__[attr]; idsc = cls.__dict__[iattr]
        dscget = dsc.__get__; dscset = dsc.__set__; idscget = idsc.__get__; idscset = idsc.__set__
        def getter(Fp) -> vector: """get vector"""; idx = idscget(Fp); return None if idx is None else dscget(Fp)(idx)
        def setter(Fp, val: iterable):
            """set vector"""
            if val is None: VIset(Fp,val)
            else:
                if idscget(Fp) is None: VIset(Fp,dscget(Fp).new(val).Index)
                else: dscget(Fp)[idscget(Fp)] = val
        cls.__dict__[attr] = property(getter, setter)
        def isetter(Fp, val: (int, None)):
            """set index"""
            val = getattr(val,'__value__',val)
            if val.__class__ in {str,int,float}: val = int(val)
            elif val is not None: print('ERROR: %s.%s received an invalid value (%s)'%(name,attr,val))
            idscset(Fp,val)
        cls.__dict__[iattr] = property(idscget, isetter)
        return dscset, idscset
    
    def multiprop( cls, attr, iattr ) -> ( function, function ):
        """multi value/index"""
        name = Facepoint.__name__
        dsc = cls.__dict__[attr]; idsc = cls.__dict__[iattr]
        dscget = dsc.__get__; dscset = dsc.__set__; idscget = idsc.__get__; idscset = idsc.__set__
        def setter(Fp, val: iterable): """set channeled vectors"""; dscget(Fp)[:] = val
        def isetter(Fp, val: iterable): """set channeled indices"""; idscget(Fp)[:] = val
        cls.__dict__[attr] = property(dscget, setter)
        cls.__dict__[iattr] = property(idscget, isetter)
        return dscset, idscget, idscset
    
    Vset, VIset = singleProp(   Facepoint, 'Vertice',   'VerticeIndex'      )
    Nset, NIset = singleProp(   Facepoint, 'Normal',    'NormalIndex'       )
    Bset, BIset = singleProp(   Facepoint, 'BiNormal',  'BiNormalIndex'     )
    Tset, TIset = singleProp(   Facepoint, 'Tangent',   'TangentIndex'      )
    Cset, CIget, CIset = multiprop(    Facepoint, 'Colors'     )
    Uset, UIget, UIset = multiprop(    Facepoint, 'UVs'        )
    Wset, WIget, WIset = multiprop(    Facepoint, 'Weights'    )
    Mset, MIget, MIset = multiprop(    Facepoint, 'Materials'  )

    # Facepoint.*Vector* >>> vector(0,0(,0(,1))) if not defined
    # Facepoint.*Vector* = (0,0,0,1)
    # if you change the index, the vector will change
    # if you change the vector, the index may change
    
    class Primitive(UGEObject):
        """UGE Primitive"""
        __public__={'Type':{'w'},'FacepPoints':{'w','p'}}
        __disabled__ = {'Name'}
        def __new__(cls,*other: tuple ):
            Pr = UGEObject.__new__(cls)
            Pr.Type = None
            FPset( Pr, UGECollection(Pr,Facepoint,True ) )
        
        def new(cls, parents: mappingproxy, holder: UGECollection, item, Index, *args, **kw):
            """Create a new primitive instance of the specified type"""
            Pr = cls.__new__(parents,holder,Index,*args,**kw)
            Pr.Type = item
            return Pr
        
    globals()['Primitive'] = Primitive
    
    FPset = CollectionProp( Primitive, 'Facepoints' )
        
    class mesh(object):
        """mesh Type"""
        __slots__=['Name','Vertices','Normals','BiNormals','Tangents','Colors','UVs','Weights','Primitives']
        def __init__(Me,Ob: UGEObject):
            Me.Name=Ob.Name
            
            Me.Vertices = UGECollection(Ob,vector)
            Me.Normals  = UGECollection(Ob,vector)
            Me.BiNormals= UGECollection(Ob,vector) # NOTE: some sources (such as the IQM demo) call these BiTangents
            Me.Tangents = UGECollection(Ob,vector)
            Me.Colors   = UGEChannels(Ob,vector)
            Me.UVs      = UGEChannels(Ob,vector)
            Me.Weights  = UGECollection(Ob,float)
            
            Me.Primitives = UGECollection(Ob,Primitive,True,True )
        __eq__ = lambda this,other: this.Name == other or this is other
        __ne__ = lambda this,other: this.Name != other and this is not other
    globals()['mesh'] = mesh
private()
del private
# noinspection PyUnresolvedReferences
from . import Facepoint, Primitive, mesh # IDEA can't comprehend dynamics

objectextension=extension('Object')
@objectextension
def Primitives(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.Primitives
    print('ERROR: Object.Primitives cannot be accessed for %s objects'%Ob.Type)
del Primitives

# lists
@objectextension
def Vertices(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.Vertices
    print('ERROR: Object.Vertices cannot be accessed for %s objects'%Ob.Type)
del Vertices
@objectextension
def Normals(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.Normals
    print('ERROR: Object.Normals cannot be accessed for %s objects'%Ob.Type)
del Normals
@objectextension
def BiNormals(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.BiNormals
    print('ERROR: Object.BiNormals cannot be accessed for %s objects'%Ob.Type)
del BiNormals
@objectextension
def Tangents(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.Tangents
    print('ERROR: Object.Tangents cannot be accessed for %s objects'%Ob.Type)
del Tangents
@objectextension
def Colors(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.Colors
    print('ERROR: Object.Colors cannot be accessed for %s objects'%Ob.Type)
del Colors
@objectextension
def UVs(Ob):
    if not Ob.Data: Ob.Data=mesh(Ob)
    if Ob.Type=='mesh': return Ob.Data.UVs
    print('ERROR: Object.UVs cannot be accessed for %s objects'%Ob.Type)
del UVs
'''
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMesh(MeshName="Mesh0"):
    """Creates or References a UGE Mesh in the current object
    
    usage:
    - MeshID = ugeSetMesh( "Mesh0" ) # (default) Reference or create "Mesh0"
    - MeshID = ugeSetMesh( int ) # Reference mesh by ID"""
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetMesh() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: ObjectData = CurrentObject.Data = mesh(MeshName)
    elif ObjectData!='mesh': print('ERROR: ugeSetMesh() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    Meshes = ObjectData.Meshes
    if MeshName in Meshes or MeshName.__class__ is str: Meshes.current = Meshes[MeshName]
    elif MeshName.__class__ is int: print('ERROR: ugeSetMesh() cannot find mesh ID (%i)'%MeshName)
    else: print('ERROR: ugeSetMesh() received an invalid value (%s)'%MeshName)
    ugeSetMesh.func_defaults = ("Mesh%i"%len(Meshes),)
    return Meshes.current.ID

def _localize(this): # NOTE: `this` refers to the current vector
    MeshObject = this.data
    ObjectData = MeshObject.data
    Weights = ObjectData.Weights
    Bones = [] # NOTE: Bones (if found) should be a collection instead of a list
    Parent = CurrentObject.Parent
    while Parent: # TODO: catalog the _rig object instead of searching for it every time
        if Parent.Data=='_rig': Bones = Parent.Data.Bones; break
        Parent = Parent.Parent
'''
    

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetVertArr(Vertices, flag=CONST.UGE_PRETRANSFORMED):
    """Sets the vertex array of the current mesh.
    
    arguments:
    - flag = UGE_PRETRANSFORMED # vertices in edit-position (T-pose)
    - flag = UGE_UNTRANSFORMED # vertices in raw-position (ready for animation)
    
    usage:
    - ugeSetVertArr( [ [X,Y,Z,W], ... ], flag = flag )"""
    CurrentObject = FORMAT.Roots.current.Worlds.current.Scenes.current.Objects.current
    if not CurrentObject: print('ERROR: ugeSetVertArr() expected a defined object.'); return
    ObjectVertices =  CurrentObject.Vertices
    for i,V in enumerate(Vertices): ObjectVertices[i] = vector( *V, flag=flag )

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetNormalArr(Normals, flag = CONST.UGE_PRETRANSFORMED):
    """Sets the normal array of the current mesh.
    
    arguments:
    - flag = UGE_PRETRANSFORMED # normals in edit-rotation (T-pose)
    - flag = UGE_UNTRANSFORMED # normals in raw-rotation (ready for animation)
    
    usage:
    - ugeSetNormalArr( [ [I,J,K,H], ... ], flag = flag )"""
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetNormalArr() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: ObjectData = CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetNormalArr() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    normalArray = map(vector,Normals)
    blankArray = [None]*len(normalArray)
    if flag == CONST.UGE_UNTRANSFORMED: # DEPRECATED
        ObjectData.UTNormals,ObjectData.Normals = normalArray,blankArray
    else: ObjectData.Normals,ObjectData.UTNormals = normalArray,blankArray
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT], Deprecated=True)
def ugeSetUTVertArr(Verts):
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetUTVertArr() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetUTVertArr() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    CurrentObject.Data.UTVerts = map(vector,Verts) # DEPRECATED
    CurrentObject.Data.Vertices =[None]*len(Verts)
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT], Deprecated=True)
def ugeSetUTNormalArr(Normals):
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetUTNormalArr() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetUTNormalArr() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    CurrentObject.Data.UTNormals = map(vector,Normals) # DEPRECATED
    CurrentObject.Data.Normals = [None]*len(Normals)
    
# TODO: binormal, tangent, and bitangent

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetColorArr(Colors,channel=0):
    """Sets the color array of the current mesh.
    
    arguments:
    - channel = 0 # sets the UV channel (max value of 1)
    
    usage:
    - ugeSetColorArr( [ [I,A], [R,G,B,A], ... ], channel )"""
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetColorArr() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetColorArr() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    CurrentObject.Data.Colors[channel] = map(vector,Colors)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetUVArr(UVs,channel=0):
    """Sets the UV array of the current mesh.
    
    arguments:
    - channel = 0 # sets the UV channel (max value of 7)
    
    usage:
    - ugeSetUVArr( [ [S,T,R,Q], ... ], channel )"""
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetUVArr() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetUVArr() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    CurrentObject.Data.UVs[channel] = map(vector,UVs)

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetPrimitive(Primitive=CONST.UGE_TRIANGLES):
    """Creates or References a UGE Primitive
    
    usage:
    - PrimID = ugeSetPrimitive( UGE_TRIANGLES ) # (default) Creates a new triangle primitive
    - PrimID = ugeSetPrimitive( int ) # Reference primitive by ID"""
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetPrimitive() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: ObjectData = CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetPrimitive() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    Primitives = ObjectData.Meshes.current.Primitives
    if Primitive.__class__.__name__ == 'UGE_Primitive_Type':
        CurrentPrimitive = Primitives._current = Primitives['']
        CurrentPrimitive.Type = Primitive
        return CurrentPrimitive.ID
    elif Primitive in Primitives:
        CurrentPrimitive = Primitives._current = Primitives[ Primitive ]
        return CurrentPrimitive.ID
    else: print('ERROR: ugeSetPrimitive() expects a UGE Primitive or an index.'); return

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetFacepoint(FacePoint=None):
    """Creates or References a UGE FacePoint in the current primitive
    
    usage:
    - FPID = ugeSetFacepoint( None ) # (default) Creates a new FacePoint
    - FPID = ugeSetFacepoint( int ) # Reference FacePoint by ID"""
    CurrentObject = FORMAT.Roots._current.Objects._current
    if not CurrentObject: print('ERROR: ugeSetFacepoint() expected a defined object.'); return
    ObjectData = CurrentObject.Data
    if not ObjectData: ObjectData = CurrentObject.Data=mesh(CurrentObject.Name)
    elif ObjectData!='mesh': print('ERROR: ugeSetFacepoint() cannot operate on %s objects.'%ObjectData.__class__.__name__); return
    CurrentPrimitive = ObjectData.Meshes.current.Primitives._current
    if not CurrentPrimitive: print('ERROR: ugeSetFacepoint() expected a defined primitive.'); return
    FacePoints = CurrentPrimitive.FacePoints
    if FacePoint==None:
        CurrentFacePoint = FacePoints._current = FacePoints['']
        return CurrentFacePoint.ID
    elif FacePoint in FacePoints:
        CurrentFacePoint = FacePoints._current = FacePoints[FacePoint]
        return CurrentFacePoint.ID
    else: print('ERROR: ugeSetFacepoint() expects a valid index.'); return
    
# NOTE: UT functions are not needed for indices, set a UT vector array and index to that.
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetVertIndex(ID):
    """Sets the current FacePoint's vertex index
    
    usage:
    - VID = ugeSetVertIndex( 0 )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentPrimitive = CurrentObject.Data.Meshes.current.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    if ID.__class__ is int: CurrentFacePoint.VertID = ID; return ID

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetNormalIndex(ID):
    """Sets the current FacePoint's normal index
    
    usage:
    - NID = ugeSetNormalIndex( 0 )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentPrimitive = CurrentObject.Data.Meshes.current.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    if ID.__class__ is int: CurrentFacePoint.NormalID = ID; return ID

# TODO: binormal, tangent, and bitangent

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetColorIndex(ID,channel=0):
    """Sets the current FacePoint's color index
    
    arguments:
    - channel = 0 # sets the color channel (max value of 1)
    
    usage:
    - CID = ugeSetColorIndex( 0 )
    - CID = ugeSetColorIndex( 0, channel=1 )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentPrimitive = CurrentObject.Data.Meshes.current.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    if ID.__class__ is int: CurrentFacePoint.ColorIDs[channel] = ID; return ID

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetUVIndex(ID,channel=0):
    """Sets the current FacePoint's UV index
    
    arguments:
    - channel = 0 # sets the UV channel (max value of 7)
    
    usage:
    - UVID = ugeSetUVIndex( 0 )
    - UVID = ugeSetUVIndex( 0, channel=1 )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentPrimitive = CurrentObject.Data.Meshes.current.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    if ID.__class__ is int: CurrentFacePoint.UVIDs[channel] = ID; return ID

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetVert(X,Y=None,Z=None,W=None, flag = CONST.UGE_PRETRANSFORMED):
    """Applies a vertex index to the current facepoint and appends the given vertex if necessary.
    
    arguments:
    - flag = UGE_PRETRANSFORMED # (default) vertices in edit-position (T-pose)
    - flag = UGE_UNTRANSFORMED # vertices in raw-position (ready for animation)
    
    usage:
    - VID = ugeSetVert( X,Y,Z,W )
    - VID = ugeSetVert( X,Y,Z, flag = flag )
    - VID = ugeSetVert( [X,Y,Z], flag = flag )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    VertArray,OtherArray = (CurrentObject.Data.UTVerts,CurrentObject.Data.Vertices)\
        if flag == CONST.UGE_UNTRANSFORMED else (CurrentObject.Data.Vertices,CurrentObject.Data.UTVerts)
    NewVert = vector(X,Y,Z,W)
    ID = 0
    for Vert in VertArray: # iterate once, not twice (both `in` and `.index()` do this)
        if Vert==NewVert: break
        ID+=1 # if the loop completes, ID should == len(VertArray)
    else: # if not found, append the new vert (yes, loops have an else case)
        VertArray.append(NewVert); OtherArray.append(None)
    CurrentFacePoint.VertID = ID
    return ID
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetNormal(I,J=None,K=None,H=None, flag = CONST.UGE_PRETRANSFORMED):
    """Applies a normal index to the current facepoint and appends the given normal if necessary.
    
    arguments:
    - flag = UGE_PRETRANSFORMED # (default) normals in edit-rotation (T-pose)
    - flag = UGE_UNTRANSFORMED # normals in raw-rotation (ready for animation)
    
    usage:
    - NID = ugeSetNormal( I,J,K,H )
    - NID = ugeSetNormal( I,J,K, flag = flag )
    - NID = ugeSetNormal( [I,J,K], flag = flag )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    NormalArray,OtherArray = (CurrentObject.Data.UTNormals,CurrentObject.Data.Normals)\
        if flag == CONST.UGE_UNTRANSFORMED else (CurrentObject.Data.Normals,CurrentObject.Data.UTNormals)
    NewNormal = vector(I,J,K,H)
    ID = 0
    for Vert in NormalArray:
        if Vert==NewNormal: break
        ID+=1
    else: NormalArray.append(NewNormal); OtherArray.append(None)
    CurrentFacePoint.NormalID = ID
    return ID

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT], Deprecated=True)
def ugeSetUTVert(X,Y=None,Z=None,W=None):
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    NewVert = vector(X,Y,Z,W)
    ID = 0
    for Vert in CurrentObject.Data.UTVerts:
        if Vert==NewVert: break
        ID+=1
    else: CurrentObject.Data.UTVerts.append(NewVert); CurrentObject.Data.Vertices.append(None)
    CurrentFacePoint.VertID = ID
    return ID
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT], Deprecated=True)
def ugeSetUTNormal(I,J=None,K=None,H=None):
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    NewNormal = vector(I,J,K,H)
    ID = 0
    for Vert in CurrentObject.Data.UTNormals:
        if Vert==NewNormal: break
        ID+=1
    else: CurrentObject.Data.UTNormals.append(NewNormal); CurrentObject.Data.Normals.append(None)
    CurrentFacePoint.NormalID = ID
    return ID
    
# TODO: binormal, tangent, and bitangent

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetColor(R,G=None,B=None,A=None, channel=0):
    """Applies a color index to the current facepoint and appends the given color if necessary.
    
    arguments:
    - channel = 0 # sets the color channel (max value of 1)
    
    usage:
    - CID = ugeSetColor( R,G,B,A )
    - CID = ugeSetColor( [R,G,B], channel=1 )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    Colors = CurrentObject.Data.Colors
    if channel in Colors: ColorArray = Colors[channel]
    else: ColorArray = Colors[channel] = []
    NewColor = vector(R,G,B,A)
    ID = 0
    for Vert in ColorArray:
        if Vert==NewColor: break
        ID+=1
    else: ColorArray.append(NewColor)
    CurrentFacePoint.ColorIDs[channel] = ID
    return ID
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetUV(S,T=None,R=None,Q=None, channel=0):
    """Applies a UV index to the current facepoint and appends the given UV if necessary.
    
    arguments:
    - channel = 0 # sets the UV channel (max value of 7)
    
    usage:
    - UVID = ugeSetUV( S,T,R,Q )
    - UVID = ugeSetUV( [S,T], channel=1 )"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    UVs = CurrentObject.Data.UVs
    if channel in UVs: UVArray = UVs[channel]
    else: UVArray = UVs[channel] = []
    NewUV = vector(S,T,R,Q)
    ID = 0
    for Vert in UVArray:
        if Vert==NewUV: break
        ID+=1
    else: UVArray.append(NewUV)
    CurrentFacePoint.UVIDs[channel] = ID
    return ID
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetWeight(Bone, Value=1.0):
    """Appends the BoneID and the index of the given weight-value to the current facepoint.
    
    usage:
    - WID = ugeSetWeight( 'BoneName', 1.0 )
    - WID = ugeSetWeight( int, 1.0 ) # BoneID"""
    Objects = FORMAT.Roots._current.Objects
    if not Objects.objects: return # TODO: notify developer to define an object
    CurrentObject = Objects._current
    if not CurrentObject.Data: CurrentObject.Data=mesh(CurrentObject.Name)
    elif CurrentObject.Data!=mesh: return # TODO: notify developer a mesh object is expected
    CurrentMesh = CurrentObject.Data.Meshes.current
    CurrentPrimitive = CurrentMesh.Primitives._current
    if not CurrentPrimitive: return # TODO: notify developer to define a primitive
    CurrentFacePoint = CurrentPrimitive.FacePoints._current
    if not CurrentFacePoint: return # TODO: notify developer to define a facepoint
    
    Bones = []
    # find the root _rig used by the current object (if any) or create it if possible
    # TODO: deal with bone references from multiple hierarchical _rig objects 
    Parent = CurrentObject.Parent
    while Parent: # TODO: catalog the _rig object instead of searching for it every time
        if Parent.Data=='_rig': Bones = Parent.Data.Bones; break
        Parent = Parent.Parent
    Bone = getattr(Bone, '__value__', Bone)
    if Bones and Bone in Bones or Bone.__class__ is str: Bone = Bones[Bone].ID
    elif Bone.__class__ is int: return # TODO: notify developer of the invalid ID

    Value = getattr(Value, '__value__', Value)
    if Value.__class__!=float:
        try: Value=float(Value)
        except (TypeError,ValueError): print('ERROR: ugeSetWeight() expects a float value.'); return
        if not 0.0>=Value<=1.0: print('ERROR: ugeSetWeight() %s is not in range 0.0 to 1.0.'%Value); return
    
    Weights = CurrentObject.Data.Weights
    WeightID = 0
    for WeightValue in Weights:
        if WeightValue==Value: break
        WeightID+=1
    else: Weights.append(Value)
    
    WeightIDs = CurrentFacePoint.WeightIDs
    IDs = [Bone,WeightID]
    if IDs not in WeightIDs: WeightIDs.append(IDs)
    return WeightID
    