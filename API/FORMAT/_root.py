# -*- coding: utf-8 -*-
"""UGE Root class and associate functions"""

from . import ugeSetWorld, ugeSetScene, ugeSetObject
from .. import CONST, UGE_GLOBAL_WRAPPER, register

def private():
    """private namespace"""
    from . import World, Scene, Object, Material, Shader, Texture, Image
    from ..OBJECT import UGEObject, newUGEObject, UGECollection, CollectionProp
    
    class Root(UGEObject):
        """UGE Root"""
        __public__ = {'Worlds':{'p','w'}, 'Scenes':{'p','w'}, 'Materials':{'p','w'}, 'Shaders':{'p','w'}, 'Textures':{'p','w'}, 'Images':{'p','w'}, 'Objects':{'p','w'}}
        # noinspection PyUnusedLocal
        def __new__(cls,*other: tuple):
            Rt = newUGEObject(cls,*other)
            # noinspection PyStatementEffect
            Rt.Worlds['UGE_Default_World'].Scenes["UGE_Default_Scene"]
            return Rt
    
    CollectionProp( Root, 'Scenes',     Scene,    __builtin__ = "CurrentScene" )
    CollectionProp( Root, 'Worlds',     World,    __builtin__ = "CurrentWorld" )
    CollectionProp( Root, 'Materials',  Material, __builtin__ = "CurrentMaterial" )
    CollectionProp( Root, 'Shaders',    Shader,   __builtin__ = "CurrentShader" )
    CollectionProp( Root, 'Textures',   Texture,  __builtin__ = "CurrentTexture" )
    CollectionProp( Root, 'Images',     Image,    __builtin__ = "CurrentImage" )
    CollectionProp( Root, 'Objects',    Object,   __builtin__ = "CurrentObject" )
    
    return Root, UGECollection( None, Root, __builtin__ = "CurrentRoot" )

Root, Roots = private()
del private
validRootTypes = {str,Root,Root.__proxy__}

# for SES/UI usage:
# noinspection PyStatementEffect
def ugeSetRoot(RootName: (str, Root)) -> Root:
    """Creates or References a Root"""
    RootName = getattr(RootName, '__value__', RootName)
    if RootName.__class__ in validRootTypes:
        Roots[RootName]
        ugeSetWorld.__defaults__ = ("World%i"%len(CurrentRoot.Worlds),)
        ugeSetScene.__defaults__ = ("Scene%i"%len(CurrentRoot.Scenes),)
        ugeSetObject.__defaults__ = ("Object%i"%len(CurrentRoot.Objects),)
        return CurrentRoot
    else: print('ERROR: ugeSetRoot() received an invalid value (%s)'%RootName)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeGetRootName(RootObject: (Root, None) = None ) -> str:
    """Returns the Name of the current or given Root."""
    if RootObject in validRootTypes and RootObject is not str: return RootObject.Name
    return CurrentRoot.Worlds( RootObject ).Name
    
def ugeDeleteRoot(RootName: (str, Root)) -> None:
    """Clear all references to and from Root"""
    del Roots[RootName]

def ugeCopyRoot(root1: Root, root2: Root) -> None:
    """Copy root2 into root1"""
    root1Scenes = root1.Scenes
    root1Has = root1Scenes.__contains__
    for CurrentScene in root2.Scenes:
        if root1Has(CurrentScene): continue # root already has a copy of this scene
        Name = CurrentScene.Name
        if root1Has(Name): # avoid duplicate names
            i=1
            while root1Has( CurrentScene.Name ): CurrentScene.Name='%s.%03i'%(Name,i); i+=1 # rename until we have a new name
        CurrentScene.ID(len(root1Scenes))
        root1Scenes.append(CurrentScene)
        
    root1Objects = root1.Objects
    root1Has = root1Objects.__contains__
    for CurrentObject in root2.Objects:
        if root1Has(CurrentObject): continue # root already has a copy of this object
        Name = CurrentObject.Name
        if root1Has(Name): # avoid duplicate names
            i=1
            while root1Has( CurrentObject.Name ): CurrentObject.Name='%s.%03i'%(Name,i); i+=1 # rename until we have a new name
        CurrentObject.ID(len(root1Objects))
        root1Objects.append(CurrentObject)

    # TODO: Materials, Textures, and Images
    # TODO: advanced copy with data comparison (optional discards for similar data)

def ugeMergeRoots(root1: Root, root2: Root) -> None:
    """Merge root2 into root1"""
    ugeCopyRoot(root1, root2)
    ugeDeleteRoot(root2)
