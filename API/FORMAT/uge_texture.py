# -*- coding: utf-8 -*-
"""UGE Texture class and associate functions"""

from .. import UGE_GLOBAL_WRAPPER, register
from ..CONST import UGE_MODEL_SCRIPT

# noinspection PyShadowingNames
def private():
    """private namespace"""
    
    from ..OBJECT import UGEObject, CollectionProp

    #CONST.define( '''
    #        UGE_TEX_2D
    #        '''.split(), type('UGE_TextureParam_Target', (CONST.UGE_CONSTANT,), {}), [ CONST.UGE_MODEL_SCRIPT ])
    #CONST.define( '''
    #        UGE_TEX_WRAP_S
    #        UGE_TEX_WRAP_T
    #        '''.split(), type('UGE_TextureParam_Name', (CONST.UGE_CONSTANT,), {}), [ CONST.UGE_MODEL_SCRIPT ])
    #CONST.define( '''
    #        UGE_TEX_CLAMP_EDGE
    #        UGE_TEX_REPEAT
    #        UGE_TEX_MIRRORED_REPEAT
    #        '''.split(), type('UGE_TextureParam', (CONST.UGE_CONSTANT,), {}), [ CONST.UGE_MODEL_SCRIPT ])
    #
    #class Param(UGEObject):
    #    """UGE Texture Param"""
    #    __public__ ={'Target':{'p'},'Name':{'p'},'Param':{'p'}}
    #    def __init__(Pm,*other):
    #        Pm.Target=None
    #        Pm.Name=None
    #        Pm.Param=None
    
    class Texture(UGEObject):
        """UGE Texture"""
        __slots__ = ['Images']
        #def __new__(cls, *other: tuple, **kw ):
        #    Tx=newUGEObject(cls,*other)
        #    return Tx
            
    CollectionProp( Texture, 'Images' )
    
    return Texture

Texture = private()
del private
validTextureTypes = {str,Texture}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([UGE_MODEL_SCRIPT])
def ugeSetTexture(TextureName: (str, Texture) = "Texture0", assign: bool = True ) -> Texture:
    """Creates or References a Texture and optionally assigns it to the current Material."""
    TextureName = getattr(TextureName, '__value__', TextureName)
    if TextureName.__class__ in validTextureTypes:
        CurrentMaterial.Textures[TextureName] if assign and CurrentMaterial else CurrentRoot.Textures[TextureName]
        ugeSetTexture.func_defaults=( "Texture%i"%len(CurrentRoot.Textures), True )
        return CurrentTexture
    else: print('ERROR: ugeSetTexture() received an invalid value (%s)'%TextureName)

#@UGE_GLOBAL_WRAPPER
#@register([CONST.UGE_MODEL_SCRIPT])
#def ugeSetTexParam(Target,Name,Param):
#    """[Low Level Function] Applies a texture parameter to the current texture
#    (NOTE: refer to the OpenGL Fixed Function documentation for information on constants used with this function)
#
#    usage:
#    - ugeSetTexParam( Target, Name, Param )"""
#    CurrentTexture = FORMAT.Roots._current.Textures._current
#    if not CurrentTexture: print('WARNING: ugeSetTexParam() )expected a defined texture.'); return
#    CurrentTexture.Params.append([Target,Name,Param])

#def ugeSetTexEnv():