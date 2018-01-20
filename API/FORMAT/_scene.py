# -*- coding: utf-8 -*-
"""UGE Scene class and associate functions"""

from .. import CONST, UGE_GLOBAL_WRAPPER, register
from ..OBJECT import UGEObject, UGECollection, CollectionProp

class Scene(UGEObject):
    """UGE Scene"""
    __public__ = {'Objects':{'p','w'}}
    # noinspection PyUnusedLocal
    def __init__(Sc,*other: tuple ):
        Rt = Sc.__parent__
        Sc.Objects = UGECollection( Sc, Rt.Objects )

CollectionProp( Scene, 'Objects' )

validSceneTypes = {str,Scene,Scene.__proxy__}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetScene(SceneName: (str, Scene) = "Scene0") -> Scene:
    """Creates or References a Scene"""
    SceneName = getattr(SceneName, '__value__', SceneName)
    if SceneName.__class__ in validSceneTypes:
        CurrentRoot.Scenes[SceneName]
        ugeSetScene.__defaults__=("Scene%i"%len(CurrentRoot.Scenes),)
        return CurrentScene
    else: print('ERROR: ugeSetScene() received an invalid value (%s)'%SceneName)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetScenes() -> UGECollection: # TODO: return scenes from current, specified, or given world
    """Returns the current Root's Scenes."""
    return CurrentRoot.Scenes

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetSceneName(SceneObject: (Scene, None) = None) -> str:
    """Returns the Name of the current or given Scene."""
    if SceneObject is None or SceneObject.__class__ in validSceneTypes: return CurrentRoot.Scenes(SceneObject).Name
    else: print('ERROR: ugeGetSceneName() received an invalid value (%s)'%SceneObject)