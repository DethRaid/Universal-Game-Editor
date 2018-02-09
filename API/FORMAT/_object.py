# -*- coding: utf-8 -*-
"""UGE Object class and associate functions"""

from . import Root, Scene, vector
from . import validSceneTypes, ugeSetBone, VectorProp
from .. import UGE_GLOBAL_WRAPPER, register
from ..CONST import UGE_MODEL_SCRIPT

# noinspection PyShadowingNames
def private():
    """private namespace"""
    from ..OBJECT import UGEObject, Hierarchical, UGECollection, IntProp, CollectionProp
    
    #CONST.define( '''
    #        UGE_EULER
    #        UGE_QUAT
    #        '''.split(), type('UGE_Rotation', (CONST.UGE_CONSTANT,), {}), [ UGE_MODEL_SCRIPT ])
    
    #from CONST import UGE_EULER, UGE_QUAT
    
    class Object(UGEObject, Hierarchical):
        """UGE Object"""
        __public__ = {'Viewport':{'w'},'Location':{'p','w'},'Rotation':{'p','w'},'Scale':{'p','w'},'Materials':{'p','w'},'Type':set(),'SubName':{'w'}}
        __slots__ = ['Data', 'Viewport', 'Location', 'Rotation', 'Scale', 'Materials']
        
        # noinspection PyUnusedLocal, PyDunderSlots, PyUnresolvedReferences
        def __init__(Ob,*other: tuple ):
            Rt = Ob.__parent__
            Ob.Data = None
            
            Ob.Viewport  = 0
            Ob.Location  = (0,0,0)
            Ob.Rotation  = (0,0,0)
            Ob.Scale     = (1,1,1)
        
        Type = property( lambda this: this.Data.__class__.__name__ if this.Data else None ) # type: str -> (str, None)
        SubName = property(
            lambda this: this.Data.Name if this.Data else this.Name, # returning Object.Name for compatibility
            lambda this, Name: this.Data.__setattr__('Name',this.Name if Name is None else Name) )
    
    IntProp(        Object, 'Viewport'          )
    VectorProp(     Object, 'Location'          )
    VectorProp(     Object, 'Rotation'          )
    VectorProp(     Object, 'Scale'             )
    CollectionProp( Object, 'Materials', 'Root' )
    return Object

Object = private()
del private
validObjectTypes = {str,Object}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObject(ObjectName: (str, Object) = "Object0") -> Object:
    """Creates or References an Object"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes:
        CurrentScene.Objects[ObjectName]
        ugeSetObject.__defaults__ = ("Object%i"%len(CurrentScene.Objects),)
        if CurrentObject.Type=='rig': ugeSetBone.__defaults__ = ("Bone%i"%len(CurrentObject.Bones),) # TODO: update explicitely
        return CurrentObject
    else: print('ERROR: ugeSetObject() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectSubName(Name: str = None) -> None:
    """Sets the name of the current Object's subtype, or clears it to the name of the containing object."""
    if CurrentObject:
        if CurrentObject.Type:
            Name = getattr(Name, '__value__', Name)
            if Name is None: CurrentObject.SubName = CurrentObject.Name; return
            if Name.__class__ == str: CurrentObject.SubName = Name
            else: print('ERROR: ugeSetObjectSubName() received an invalid value (%s)'%Name)
        else: print('ERROR: ugeSetObjectSubName() expected a defined subtype')
    else: print('ERROR: ugeSetObjectSubName() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectParent(ObjectName: (str, Object) = None) -> None:
    """Clears the current Object's parent, or sets it to an existing object."""
    if not CurrentObject:
        ObjectName = getattr(ObjectName, '__value__', ObjectName)
        if ObjectName is None or ObjectName.__class__ in validObjectTypes: CurrentObject.Parent = ObjectName
        else: print('ERROR: ugeSetObjectParent() received an invalid value (%s)'%ObjectName)
    else: print('ERROR: ugeSetObjectParent() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectViewport(Viewport: int = 0) -> None:
    """Sets the current Object's viewport to the specified values"""
    if CurrentObject:
        Viewport = getattr(Viewport, '__value__', Viewport)
        if Viewport.__class__ == int: CurrentObject.Viewport = Viewport
        else: print('ERROR: ugeSetObjectSubName() received an invalid value (%s)'%Viewport)
    else: print('ERROR: ugeSetObjectViewport() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectLoc(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None) -> None:
    """Sets the current Object's relative location to the specified (up to 3D) values"""
    if CurrentObject: CurrentObject.transform.Location = (X,Y,Z)
    else: print('ERROR: ugeSetObjectLoc() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectLocX(X: (float, int, str)) -> None:
    """Sets the current Object's relative X location to the specified value"""
    if CurrentObject: CurrentObject.transform.Location.X = X
    else: print('ERROR: ugeSetObjectLocX() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectLocY(Y: (float, int, str)) -> None:
    """Sets the current Object's relative Y location to the specified value"""
    if CurrentObject: CurrentObject.transform.Location.Y = Y
    else: print('ERROR: ugeSetObjectLocY() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectLocZ(Z: (float, int, str)) -> None:
    """Sets the current Object's relative Z location to the specified value"""
    if CurrentObject: CurrentObject.transform.Location.Z = Z
    else: print('ERROR: ugeSetObjectLocZ() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectRot(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None) -> None:
    """Sets the current Object's relative rotation to the specified (up to 4D) values"""
    if CurrentObject: CurrentObject.transform.Rotation = (X,Y,Z,W)
    else: print('ERROR: ugeSetObjectRot() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectRotX(X: (float, int, str)) -> None:
    """Sets the current Object's relative X rotation to the specified value"""
    if CurrentObject: CurrentObject.transform.Rotation.X = X
    else: print('ERROR: ugeSetObjectRotX() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectRotY(Y: (float, int, str)) -> None:
    """Sets the current Object's relative Y rotation to the specified value"""
    if CurrentObject: CurrentObject.transform.Rotation.Y = Y
    else: print('ERROR: ugeSetObjectRotY() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectRotZ(Z: (float, int, str)) -> None:
    """Sets the current Object's relative Z rotation to the specified value"""
    if CurrentObject: CurrentObject.transform.Rotation.Z = Z
    else: print('ERROR: ugeSetObjectRotZ() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectRotW(W: (float, int, str)) -> None:
    """Sets the current Object's relative W rotation to the specified value"""
    if CurrentObject: CurrentObject.transform.Rotation.W = W
    else: print('ERROR: ugeSetObjectRotW() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectSca(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None) -> None:
    """Sets the current Object's relative scale to the specified (up to 3D) values"""
    if not CurrentObject: CurrentObject.transform.Scale = vector(X,Y,Z)
    else: print('ERROR: ugeSetObjectSca() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectScaX(X: (float, int, str)) -> None:
    """Sets the current Object's relative X scale to the specified value"""
    if CurrentObject: CurrentObject.transform.Scale.X = X
    else: print('ERROR: ugeSetObjectScaX() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectScaY(Y: (float, int, str)) -> None:
    """Sets the current Object's relative Y scale to the specified value"""
    if CurrentObject: CurrentObject.transform.Scale.Y = Y
    else: print('ERROR: ugeSetObjectScaY() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetObjectScaZ(Z: (float, int, str)) -> None:
    """Sets the current Object's relative Z scale to the specified value"""
    if CurrentObject: CurrentObject.transform.Scale.Z = Z
    else: print('ERROR: ugeSetObjectScaZ() expected a defined object')

#--- Get ---:

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjects(SceneName: (str, Scene, Root) = None):
    """returns the Objects in the given Root or current, specified, or given Scene"""
    SceneName = getattr(SceneName, '__value__', SceneName)
    if SceneName is None: return CurrentScene.Objects
    if SceneName.__class__ in validSceneTypes: return CurrentRoot.Scenes(SceneName).Objects
    elif SceneName.__class__ is Root.__proxy__: return SceneName.Objects
    else: print('ERROR: ugeGetObjects() received an invalid value (%s)'%SceneName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectViewport(ObjectName: (str, Object, None) = None) -> int:
    """returns the viewport of the current, specified, or given Object"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Viewport
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Viewport
    else: print('ERROR: ugeGetObjectViewport() received an invalid value (%s)'%ObjectName)

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectName(Object: (str, Object, None) = None) -> str:
    """returns the name of the current, specified, or given Object"""
    Object = getattr(Object, '__value__', Object)
    if Object is None: return CurrentObject.Name
    if Object.__class__ in validObjectTypes: return CurrentScene.Objects(Object).Name
    else: print('ERROR: ugeGetObjectName() received an invalid value (%s)'%Object)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectSubName(ObjectName: (str, Object, None) = None) -> str:
    """returns the name of the current, specified, or given Object's subtype"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.SubName
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).SubName
    else: print('ERROR: ugeGetObjectSubName() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectParent(ObjectName: (str, Object, None) = None) -> Object:
    """returns the current, specified, or given Object's parent Object"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Parent
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Parent.proxy
    else: print('ERROR: ugeGetObjectParent() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectLoc(ObjectName: (str, Object, None) = None) -> vector:
    """returns the current, specified, or given Object's relative location"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Location
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Location.proxy
    else: print('ERROR: ugeGetObjectLoc() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectLocX(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative X location"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Location.X
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Location.X
    else: print('ERROR: ugeGetObjectLocX() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectLocY(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative Y location"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Location.Y
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Location.Y
    else: print('ERROR: ugeGetObjectLocY() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectLocZ(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative Z location"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Location.Z
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Location.Z
    else: print('ERROR: ugeGetObjectLocZ() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectRot(ObjectName: (str, Object, None) = None) -> vector:
    """returns the current, specified, or given Object's relative rotation"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Rotation
    elif ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Rotation
    else: print('ERROR: ugeGetObjectRot() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectRotX(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative X rotation"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Rotation.X
    elif ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Rotation.X
    else: print('ERROR: ugeGetObjectRotX() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectRotY(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative Y rotation"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Rotation.Y
    elif ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Rotation.Y
    else: print('ERROR: ugeGetObjectRotY() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectRotZ(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative Z rotation"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName is None: return CurrentObject.Rotation.Z
    elif ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Rotation.Z
    else: print('ERROR: ugeGetObjectRotZ() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectRotW(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative W rotation"""
    if ObjectName is None: return CurrentObject.Rotation.W
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Rotation.quat.W
    else: print('ERROR: ugeGetObjectRotW() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectSca(ObjectName: (str, Object, None) = None) -> vector:
    """returns the current, specified, or given Object's relative scale"""
    if ObjectName is None: return CurrentObject.Scale
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Scale.proxy
    else: print('ERROR: ugeGetObjectSca() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectScaX(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative X scale"""
    if ObjectName is None: return CurrentObject.Scale.X
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Scale.X
    else: print('ERROR: ugeGetObjectScaX() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectScaY(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative Y scale"""
    if ObjectName is None: return CurrentObject.Scale.Y
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Scale.Y
    else: print('ERROR: ugeGetObjectScaY() received an invalid value (%s)'%ObjectName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetObjectScaZ(ObjectName: (str, Object, None) = None) -> (float, int):
    """returns the current, specified, or given Object's relative Z scale"""
    if ObjectName is None: return CurrentObject.Scale.Z
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Scale.Z
    else: print('ERROR: ugeGetObjectScaY() received an invalid value (%s)'%ObjectName)
