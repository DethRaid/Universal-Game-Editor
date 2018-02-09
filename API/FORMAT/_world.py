# -*- coding: utf-8 -*-
"""UGE World class and associate functions"""

from . import ugeSetScene
from .. import UGE_GLOBAL_WRAPPER, register
from ..CONST import UGE_MODEL_SCRIPT

# noinspection PyShadowingNames
def private():
    from ..OBJECT import UGEObject, CollectionProp
    
    class World(UGEObject):
        """UGE World"""
        __slots__ = ['Scenes']
        
    CollectionProp( World, 'Scenes', 'Root' )
    
    return World
World = private()
del private

validWorldTypes = {str,World}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetWorld( WorldName: (str, World) = "World0" ) -> World:
    """Creates or References a World"""
    WorldName = getattr(WorldName, '__value__', WorldName)
    if WorldName.__class__ in validWorldTypes:
        CurrentRoot.Worlds[WorldName]
        ugeSetScene.__defaults__=("Scene%i"%len(CurrentWorld.Scenes),)
        return CurrentWorld
    else: print('ERROR: ugeSetWorld() received an invalid value (%s)'%WorldName)

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetWorlds(): """Returns the current Root's Worlds."""; return CurrentRoot.Worlds

@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeGetWorldName(WorldObject: (World, None) = None) -> str:
    """Returns the Name of the current or given World."""
    if WorldObject in validWorldTypes and WorldObject is not str: return WorldObject.Name
    return CurrentRoot.Worlds(WorldObject).Name