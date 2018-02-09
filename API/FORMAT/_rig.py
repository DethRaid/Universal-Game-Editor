# -*- coding: utf-8 -*-
"""UGE Bone class and associate functions"""

from . import Object, vector
from . import validObjectTypes, VectorProp
from .. import CONST, UGE_GLOBAL_WRAPPER, register
from ..CONST import UGE_MODEL_SCRIPT

# noinspection PyShadowingNames
def private():
    """private namespace"""
    from ..OBJECT import UGEObject, Hierarchical, extension, UGECollection, IntProp, _protected
    
    # TODO: reuse these
    CONST.define( '''
            UGE_PARENT
            UGE_OBJECT
            UGE_WORLD
            UGE_INVERSE_PARENT
            UGE_INVERSE_OBJECT
            UGE_INVERSE_WORLD
            '''.split(), type('UGE_Relation', (object,), dict(__init__=lambda this,name:None)), [ CONST.UGE_MODEL_SCRIPT ])
    """
        UGE_PARENT # (default) transformations relative to parent
        UGE_OBJECT # transformations relative to containing object
        UGE_WORLD # transformations relative to world (0,0,0)
        UGE_INVERSE_PARENT
        UGE_INVERSE_OBJECT
        UGE_INVERSE_WORLD
    """
    
    class Bone(UGEObject, Hierarchical):
        """UGE Bone"""
        __public__ = {'Viewport':{'w'},'Location':{'p','w'},'Rotation':{'p','w'},'Scale':{'p','w'}}
        
        # noinspection PyUnusedLocal
        def __init__(Bn,*other: tuple ):
            Bn.Viewport = 0
            Bn.Location = (0,0,0)
            Bn.Rotation = (0,0,0)
            Bn.Scale    = (1,1,1)
    
    IntProp(    Bone, 'Viewport' )
    VectorProp( Bone, 'Location' )
    VectorProp( Bone, 'Rotation' )
    VectorProp( Bone, 'Scale' )

    new = object.__new__
    class rig(object):
        """rig Type"""
        __slots__=['Bones','Name']
        def __new__(cls,Ob: UGEObject):
            Rg = new(cls)
            Rg.Name = Ob.Name
            Rg.Bones = UGECollection( Ob, Bone, __builtin__ = 'CurrentBone' )
            return Rg
        __eq__ = lambda this,other: this.Name == other or this is other
        __ne__ = lambda this,other: this.Name != other and this is not other

    getData, setData = _protected['Object']['Data']

    objectextension = extension('Object')
    
    @objectextension
    def Bones(Ob: Object):
        """Object.Bones"""
        if Ob.Data is None: setData(Ob, rig(Ob))
        if Ob.Type=='rig': return Ob.Data.Bones
        print('ERROR: Object.Bones cannot be accessed for %s objects'%Ob.Type)
    @objectextension.setter
    def Bones(Ob: Object, val: object):
        """Object.Bones = val"""
        if getData(Ob) is None: setData(Ob,rig(Ob))
        getData(Ob).Bones[:] = val
        
    return rig, Bone

rig, Bone = private()
del private
validBoneTypes = {str,Bone}

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBone(BoneName: (str, Bone) = "Bone0") -> Bone:
    """Creates or References a Bone"""
    if CurrentObject:
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones[BoneName]
        else: print('ERROR: ugeSetBone() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeSetBone() expected a defined Object')

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneParent(BoneName: (str, Bone, None) = None) -> None:
    """clear or set the current Bone's parent"""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            BoneName = getattr(BoneName, '__value__', BoneName)
            if BoneName is None or BoneName.__class__ in validBoneTypes:
                if CurrentBone: CurrentBone.Parent = BoneName
                else: print('ERROR: ugeSetBoneParent() expected a defined Bone.')
            else: print('ERROR: ugeSetBoneParent() received an invalid value (%s)'%BoneName)
        else: print('ERROR: ugeSetBoneParent() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneParent() expected a defined Object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBonePrev(BoneName: (str, Bone, None) = None) -> None:
    """Sets the current Bone's priority in it's parent Bone's children."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            BoneName = getattr(BoneName, '__value__', BoneName)
            SetFirst = BoneName is None
            if SetFirst or BoneName.__class__ in validBoneTypes:
                if CurrentBone:
                    if SetFirst and not CurrentBone.Parent: print('ERROR: ugeSetBonePrev() cannot set first child on no parent.')
                    elif CurrentBone==BoneName: print('ERROR: ugeSetBonePrev() cannot apply current Bone as previous.')
                    else: CurrentBone.Prev = BoneName
                else: print('ERROR: ugeSetBonePrev() expected a defined Bone.')
            else: print('ERROR: ugeSetBonePrev() received an invalid value (%s)'%BoneName)
        else: print('ERROR: ugeSetBonePrev() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBonePrev() expected a defined Object')

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneLoc(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None) -> None:
    """Sets the current Bone's relative location to the specified (up to 3D) values"""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Location = (X,Y,Z)
            else: print('ERROR: ugeSetBoneLoc() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneLoc() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneLoc() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneLocX(X: (float, int, str)) -> None:
    """Sets the current Bone's relative X location to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Location.X = X
            else: print('ERROR: ugeSetBoneLocX() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneLocX() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneLocX() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneLocY(Y: (float, int, str)) -> None:
    """Sets the current Bone's relative Y location to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Location.Y = Y
            else: print('ERROR: ugeSetBoneLocY() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneLocY() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneLocY() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneLocZ(Z: (float, int, str)) -> None:
    """Sets the current Bone's relative Z location to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Location.Z = Z
            else: print('ERROR: ugeSetBoneLocZ() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneLocZ() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneLocZ() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneRot(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None, W: (float, int, str) = None) -> None:
    """Sets the current Bone's relative rotation to the specified (up to 4D) values"""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Rotation = (X,Y,Z,W)
            else: print('ERROR: ugeSetBoneRot() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneRot() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneRot() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneRotX(X: (float, int, str)) -> None:
    """Sets the current Bone's relative X rotation to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Rotation.X = X
            else: print('ERROR: ugeSetBoneRotX() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneRotX() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneRotX() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneRotY(Y: (float, int, str)) -> None:
    """Sets the current Bone's relative Y rotation to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Rotation.Y = Y
            else: print('ERROR: ugeSetBoneRotY() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneRotY() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneRotY() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneRotZ(Z: (float, int, str)) -> None:
    """Sets the current Bone's relative Z rotation to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Rotation.Z = Z
            else: print('ERROR: ugeSetBoneRotZ() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneRotZ() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneRotZ() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneRotW(W: (float, int, str)) -> None:
    """Sets the current Bone's relative W rotation to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Rotation.W = W
            else: print('ERROR: ugeSetBoneRotW() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneRotW() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneRotW() expected a defined object')

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneSca(X: (float, int, str, tuple, list), Y: (float, int, str) = None, Z: (float, int, str) = None) -> None:
    """Sets the current Bone's relative scale to the specified (up to 3D) values"""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Scale = (X,Y,Z)
            else: print('ERROR: ugeSetBoneSca() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneSca() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneSca() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneScaX(X: (float, int, str)) -> None:
    """Sets the current Bone's relative X scale to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Scale.X = X
            else: print('ERROR: ugeSetBoneScaX() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneScaX() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneScaX() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneScaY(Y: (float, int, str)) -> None:
    """Sets the current Bone's relative Y scale to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Scale.Y = Y
            else: print('ERROR: ugeSetBoneScaY() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneScaY() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneScaY() expected a defined object')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetBoneScaZ(Z: (float, int, str)) -> None:
    """Sets the current Bone's relative Z scale to the specified value."""
    if CurrentObject:
        if CurrentObject.Type == 'rig':
            if CurrentBone: CurrentBone.Scale.Z = Z
            else: print('ERROR: ugeSetBoneScaZ() expected a defined Bone.')
        else: print('ERROR: ugeSetBoneScaZ() cannot operate on %s Objects'%CurrentObject.Type)
    else: print('ERROR: ugeSetBoneScaZ() expected a defined object')

## @UGE_GLOBAL_WRAPPER
## @register([CONST.UGE_MODEL_SCRIPT])
## def ugeSetBoneBindMtx(): return 
## @UGE_GLOBAL_WRAPPER
## @register([CONST.UGE_MODEL_SCRIPT])
## def ugeSetBoneInvMtx(): return 
## @UGE_GLOBAL_WRAPPER
## @register([CONST.UGE_MODEL_SCRIPT])
## def ugeSetBoneFlag(): return

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeRigObject(ObjectName: (str, Object) = None) -> bool:
    """Tests that the current Object is a Rig"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Type=='rig'
    elif ObjectName is None:
        if CurrentObject: return CurrentObject.Type=='rig'
        else: print('ERROR: ugeRigObject() expected a defined Object'); return False
    else: print('ERROR: ugeRigObject() received an invalid value (%s)'%ObjectName); return False


#--- Get ---:


@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBones(ObjectName: (str, Object) = None):
    """returns the Bones in the current or specified Object"""
    ObjectName = getattr(ObjectName, '__value__', ObjectName)
    if ObjectName.__class__ in validObjectTypes: return CurrentScene.Objects(ObjectName).Bones
    elif ObjectName is None:
        if CurrentObject: return CurrentObject.Bones
        else: print('ERROR: ugeGetBones() expected a defined Object')
    else: print('ERROR: ugeGetBones() received an invalid value (%s)'%ObjectName)
    # noinspection PyTypeChecker
    return []

# noinspection PyShadowingNames
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneName(Bone: (str, Bone, None) = None ) -> str:
    """returns the name of the current, specified, or given Bone"""
    if CurrentObject.Type == 'rig':
        Bone = getattr(Bone, '__value__', Bone)
        if Bone is None: return CurrentObject.Bones.current.Name
        if Bone.__class__ in validBoneTypes: return CurrentObject.Bones.current(Bone).Name
        else: print('ERROR: ugeGetBoneName() received an invalid value (%s)'%Bone)
    else: print('ERROR: ugeGetBoneName() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneViewport(BoneName: (str, Bone, None) = None) -> vector:
    """returns the current, specified, or given Bone's relative location"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Viewport
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Viewport
        else: print('ERROR: ugeGetBoneViewport() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneViewport() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneParent(BoneName: (str, Bone, None) = None ) -> Bone:
    """returns the current, specified, or given Bone's parent Bone"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Parent
        if BoneName.__class__ in validObjectTypes: return CurrentObject.Bones(BoneName).Parent
        else: print('ERROR: ugeGetBoneParent() received an invalid value (%s)'%BoneName )
    else: print('ERROR: ugeGetBoneParent() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneChild(BoneName: (str, Bone, None) = None ) -> Bone:
    """returns the current, specified, or given Bone's parent Bone"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Child
        if BoneName.__class__ in validObjectTypes: return CurrentObject.Bones(BoneName).proxy.Child
        else: print('ERROR: ugeGetBoneChild() received an invalid value (%s)'%BoneName )
    else: print('ERROR: ugeGetBoneChild() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBonePrev(BoneName: (str, Bone, None) = None ) -> Bone:
    """returns the current, specified, or given Bone's parent Bone"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Prev
        if BoneName.__class__ in validObjectTypes: return CurrentObject.Bones(BoneName).proxy.Prev
        else: print('ERROR: ugeGetBonePrev() received an invalid value (%s)'%BoneName )
    else: print('ERROR: ugeGetBonePrev() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneNext(BoneName: (str, Bone, None) = None ) -> Bone:
    """returns the current, specified, or given Bone's parent Bone"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Next
        if BoneName.__class__ in validObjectTypes: return CurrentObject.Bones(BoneName).proxy.Next
        else: print('ERROR: ugeGetBoneNext() received an invalid value (%s)'%BoneName )
    else: print('ERROR: ugeGetBoneNext() cannot operate on %s Objects'%CurrentObject.Type)


@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneLoc(BoneName: (str, Bone, None) = None) -> vector:
    """returns the current, specified, or given Bone's relative location"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Location
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Location.proxy
        else: print('ERROR: ugeGetBoneLoc() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneLoc() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneLocX(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative X location"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Location.X
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Location.X
        else: print('ERROR: ugeGetBoneLocX() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneLocX() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneLocY(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative Y location"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Location.Y
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Location.Y
        else: print('ERROR: ugeGetBoneLocY() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneLocY() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneLocZ(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative Z location"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Location.Z
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Location.Z
        else: print('ERROR: ugeGetBoneLocZ() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneLocZ() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneRot(BoneName: (str, Bone, None) = None) -> vector:
    """returns the current, specified, or given Bone's relative rotation"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Rotation
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Rotation
        else: print('ERROR: ugeGetBoneRot() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneRot() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneRotX(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative X rotation"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Rotation.X
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Rotation.X
        else: print('ERROR: ugeGetBoneRotX() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneRotX() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneRotY(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative Y rotation"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Rotation.Y
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Rotation.Y
        else: print('ERROR: ugeGetBoneRotY() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneRotY() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneRotZ(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative Z rotation"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Rotation.Z
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Rotation.Z
        else: print('ERROR: ugeGetBoneRotZ() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneRotZ() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneRotW(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative W rotation"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Rotation.W
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Rotation.W
        else: print('ERROR: ugeGetBoneRotW() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneRotW() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneSca(BoneName: (str, Bone, None) = None) -> vector:
    """returns the current, specified, or given Bone's relative scale"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Scale
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Scale
        else: print('ERROR: ugeGetBoneSca() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneSca() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneScaX(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative X scale"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Scale.X
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Scale.X
        else: print('ERROR: ugeGetBoneScaX() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneScaX() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneScaY(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative Y scale"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Scale.Y
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Scale.Y
        else: print('ERROR: ugeGetBoneScaY() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneScaY() cannot operate on %s Objects'%CurrentObject.Type)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetBoneScaZ(BoneName: (str, Bone, None) = None) -> (float, int):
    """returns the current, specified, or given Bone's relative Z scale"""
    if CurrentObject.Type == 'rig':
        BoneName = getattr(BoneName, '__value__', BoneName)
        if BoneName is None: return CurrentBone.Scale.Z
        if BoneName.__class__ in validBoneTypes: return CurrentObject.Bones(BoneName).Scale.Z
        else: print('ERROR: ugeGetBoneScaY() received an invalid value (%s)'%BoneName)
    else: print('ERROR: ugeGetBoneScaZ() cannot operate on %s Objects'%CurrentObject.Type)

## @UGE_GLOBAL_WRAPPER
## @register([CONST.UGE_MODEL_SCRIPT])
## def ugeGetBoneBindMtx(): return 
## @UGE_GLOBAL_WRAPPER
## @register([CONST.UGE_MODEL_SCRIPT])
## def ugeGetBoneInvMtx(): return 
## @UGE_GLOBAL_WRAPPER
## @register([CONST.UGE_MODEL_SCRIPT])
## def ugeHasBoneFlag(): return