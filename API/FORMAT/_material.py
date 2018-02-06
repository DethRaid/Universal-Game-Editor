# -*- coding: utf-8 -*-
"""UGE Material class and associate functions"""

from . import VectorProp
from .. import CONST, UGE_GLOBAL_WRAPPER, register

# noinspection PyShadowingNames
def private():
    """private namespace"""
    from ..OBJECT import UGEObject, newUGEObject, FloatProp, CollectionProp
    
    class Material(UGEObject):
        """UGE Material"""
        __slots__ = ['Ambient', 'Diffuse', 'Specular', 'Emmisive', 'Glossiness', 'Shaders', 'Textures']
        def __new__(cls, *other: tuple, **kw ):
            Ma=newUGEObject(cls,*other)
            Ma.Ambient = (1.,1.,1.,1.)
            Ma.Diffuse = (1.,1.,1.,1.)
            Ma.Specular = (.5,.5,.5,1.)
            Ma.Emissive = (0.,0.,0.,0.)
            Ma.Glossiness = 25.0
            return Ma
    
    VectorProp(     Material, 'Ambient' )
    VectorProp(     Material, 'Diffuse' )
    VectorProp(     Material, 'Specular' )
    VectorProp(     Material, 'Emissive' )
    FloatProp(      Material, 'Glossiness' )
    CollectionProp( Material, 'Shaders', 'Root' )
    CollectionProp( Material, 'Textures', 'Root' )
    
    return Material

Material = private()
del private
validMaterialTypes = {str,Material,Material.__proxy__}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMaterial(MaterialName: (str, Material) = "Material0", assign: bool = True) -> Material:
    """Creates or References a Material and optionally assigns it to the current Object."""
    MaterialName = getattr(MaterialName, '__value__', MaterialName)
    if MaterialName.__class__ in validMaterialTypes:
        CurrentObject.Materials[MaterialName] if assign and CurrentObject else CurrentRoot.Materials[MaterialName]
        ugeSetMaterial.func_defaults=( "Material%i"%len(CurrentRoot.Materials), True )
        return CurrentMaterial
    else: print('ERROR: ugeSetMaterial() received an invalid value (%s)'%MaterialName)

@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMatAmbient(R: (float, int, str, tuple, list), G: (float, int, str) = None, B: (float, int, str) = None, A: (float, int, str) = None) -> None:
    """Sets the current Material's ambient color (where no light shines)"""
    if CurrentMaterial: CurrentMaterial.Ambient = (R,G,B,A)
    else: print('ERROR: ugeSetMatAmbient() expected a defined Material')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMatDiffuse(R: (float, int, str, tuple, list), G: (float, int, str) = None, B: (float, int, str) = None, A: (float, int, str) = None) -> None:
    """Sets the current Material's diffuse color (where indirect light shines)"""
    if CurrentMaterial: CurrentMaterial.Diffuse = (R,G,B,A)
    else: print('ERROR: ugeSetMatDiffuse() expected a defined Material')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMatSpecular(R: (float, int, str, tuple, list), G: (float, int, str) = None, B: (float, int, str) = None, A: (float, int, str) = None) -> None:
    """Sets the current Material's specular color (where direct light shines)"""
    if CurrentMaterial: CurrentMaterial.Specular = (R,G,B,A)
    else: print('ERROR: ugeSetMatSpecular() expected a defined Material')
    
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMatEmmissive(R: (float, int, str, tuple, list), G: (float, int, str) = None, B: (float, int, str) = None, A: (float, int, str) = None) -> None:
    """Sets the current Material's emissive color (glow)"""
    if CurrentMaterial: CurrentMaterial.Emmissive = (R,G,B,A)
    else: print('ERROR: ugeSetMatEmmissive() expected a defined Material')

# noinspection PyUnresolvedReferences
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetMatGlossiness(V: (float, int, str) = 25.0) -> None:
    """Sets the current Material's specular expoinent (shininess)"""
    if CurrentMaterial:
        V = getattr(V, '__value__', V)
        if V.__class__ is str: V = float(V)
        if numType(V.__class__): CurrentMaterial.Shine = V
        else: print('ERROR: ugeSetMatGlossiness() received an invalid value (%s)'%V)
    else: print('ERROR: ugeSetMatGlossiness() expected a defined Material')