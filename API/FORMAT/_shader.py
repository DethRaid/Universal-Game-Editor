# -*- coding: utf-8 -*-
"""UGE Shader class and associate functions"""

from . import Texture, vector
from .. import CONST, UGE_GLOBAL_WRAPPER, register
from ..OBJECT import UGEObject, UGECollection

class Shader(UGEObject):
    """UGE Shader"""
    __public__ = {}
    # noinspection PyUnusedLocal
    def __init__(Sh,*other: tuple ):
        pass

validShaderTypes = {str,Shader,Shader.__proxy__}

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