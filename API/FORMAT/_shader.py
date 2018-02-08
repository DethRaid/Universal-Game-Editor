# -*- coding: utf-8 -*-
"""UGE Shader class and associate functions"""

from . import Texture, vector
from .. import CONST, UGE_GLOBAL_WRAPPER, register

# noinspection PyShadowingNames
def private():
    """private namespace"""
    from ..OBJECT import UGEObject, newUGEObject, UGECollection
    from ..FILE import ugeImportFile
    
    class Shader(UGEObject):
        """UGE Shader"""
        __slots__ = {}
        def __new__(cls, *other: tuple, **kw ):
            Sh=newUGEObject(cls,*other)
            return Sh
    
        def new(cls, parents: mappingproxy, holder: UGECollection, item, external=False, *args, **kw):
            """Create a new Shader instance, optionally using the name to reference an external file."""
            Sh = cls.__new__(parents,holder,*args,**kw)
            item = getattr(item,'__value__',item) # from UGE data-type (struct or such)
            if item.__class__ is dict: Sh[:] = item
            elif external: ugeImportFile(item,CONST.UGE_MATERIAL_SCRIPT)
            return Sh

    return Shader

Shader = private()
del private
validShaderTypes = {str,Shader}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetShader(ShaderName: (str, Shader) = "Shader0", assign: bool = True ) -> Shader:
    """Creates or References a Shader and optionally assigns it to the current Material."""
    ShaderName = getattr(ShaderName, '__value__', ShaderName)
    if ShaderName.__class__ in validShaderTypes:
        CurrentMaterial.Shaders[ShaderName] if assign and CurrentMaterial else CurrentRoot.Shaders[ShaderName]
        ugeSetShader.func_defaults=( "Shader%i"%len(CurrentRoot.Shaders), True )
        return CurrentShader
    else: print('ERROR: ugeSetShader() received an invalid value (%s)'%ShaderName)