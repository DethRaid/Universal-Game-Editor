# -*- coding: utf-8 -*-
"""UGE Image class and associate functions"""

from . import vector
from .. import CONST, UGE_GLOBAL_WRAPPER, register

# noinspection PyShadowingNames
def private():
    """private namespace"""
    from ..OBJECT import UGEObject, newUGEObject, IntProp, CollectionProp
    from ..FILE import ugeImportFile

    class Image(UGEObject):
        """UGE Image Object"""
        __slots__ = ['Width','Height','Pixels','Colors']
        def __new__(cls,*other: tuple, **kw):
            Im = newUGEObject(cls,*other)
            Im.Width = 1
            Im.Height = 1
            return Im

        def new(cls, parents: mappingproxy, holder: UGECollection, item, external=False, *args, **kw):
            """Create a new Image instance, optionally using the name to reference an external file."""
            Im = cls.__new__(parents,holder,*args,**kw)
            item = getattr(item,'__value__',item) # from UGE data-type (struct or such)
            if item.__class__ is dict: Im[:] = item
            elif external: ugeImportFile(item,UGE_IMAGE_SCRIPT)
            return Im

    IntProp(        Image, 'Width' )
    IntProp(        Image, 'Height' )
    CollectionProp( Image, 'Pixels', vector ) # vector( II/R(, A/G(, B(, A ))) )
    CollectionProp( Image, 'Colors', vector ) # vector( I/R(, A/G(, B(, A ))) )
    
    setPixels = Image.Pixels.__set__
    setColors = Image.Colors.__set__
    def PixelsSetter(obj,val) -> None:
        """set Image Pixels"""
        val = getattr(val,'__value__',val)
        vtype = val.__class__
        if vtype is str: ugeImportFile(val,CONST.UGE_IMAGE_SCRIPT)
        elif '__iter__' in vtype.__dict__ or hasattr(val,'__iter__'): setPixels(obj,val)
        else: print('ERROR: Image.Pixels received an invalid value (%s)'%val.__class__)
    Image.Pixels.__init__(Image.Pixels.__get__, PixelsSetter)
    def ColorsSetter(obj,val) -> None:
        """set Image Colors"""
        val = getattr(val,'__value__',val)
        vtype = val.__class__
        if vtype is str: ugeImportFile(val,CONST.UGE_PALETTE_SCRIPT)
        elif '__iter__' in vtype.__dict__ or hasattr(val,'__iter__'): setColors(obj,val)
        else: print('ERROR: Image.Colors received an invalid value (%s)'%val.__class__)
    Image.Colors.__init__(Image.Colors.__get__, ColorsSetter)
    
    return Image
Image = private()
del private

validImageTypes = {str,Image,Image.__proxy__}

# noinspection PyStatementEffect
@UGE_GLOBAL_WRAPPER
@register([CONST.UGE_MODEL_SCRIPT])
def ugeSetImage(ImageName: (str, Image) = "Image0", assign: bool = True ) -> Image:
    """Creates or References an Image and optionally assigns it to the current Texture."""
    ImageName = getattr(ImageName, '__value__', ImageName)
    if ImageName in validImageTypes:
        CurrentTexture.Images[ImageName] if CurrentTexture and assign else CurrentRoot.Images[ImageName]
        ugeSetImage.func_defaults=( "Image%i"%len(CurrentRoot.Images), True )
        return CurrentImage
    else: print('ERROR: ugeSetImage() received an invalid value (%s)'%ImageName)

@UGE_GLOBAL_WRAPPER
@register([
    CONST.UGE_MODEL_SCRIPT,
    CONST.UGE_IMAGE_SCRIPT
    ])
def ugeSetImageWidth(W: (int, str) = 1) -> None:
    """Sets the current image's width (in pixels)"""
    if CurrentImage:
        W = getattr(W, '__value__', W) # from UGE data-type (bu32 or such)
        if W.__class__ is str: W = float(W) if '.' in W else int(W)
        if numtype(W.__class__): CurrentImage.Width = W
        else: print('ERROR: ugeSetImageWidth() received an invalid value (%s)'%W)
    else: print('ERROR: ugeSetImageWidth() expected a defined image.')

@UGE_GLOBAL_WRAPPER
@register([
    CONST.UGE_MODEL_SCRIPT,
    CONST.UGE_IMAGE_SCRIPT
    ])
def ugeSetImageHeight(H: (int, str) = 1) -> None:
    """Sets the current image's height (in pixels)"""
    if CurrentImage:
        H = getattr(H, '__value__', H) # from UGE data-type (bu32 or such)
        if H.__class__ is str: H = float(H) if '.' in H else int(H)
        if numtype(H.__class__): CurrentImage.Height = H
        else: print('ERROR: ugeSetImageHeight() received an invalid value (%s)'%H)
    else: print('ERROR: ugeSetImageHeight() expected a defined image.')

@UGE_GLOBAL_WRAPPER
@register([
    CONST.UGE_MODEL_SCRIPT,
    CONST.UGE_IMAGE_SCRIPT
    ])
def ugeSetImagePixels(Pixels: str or [vector] = [[255,255,255,255]] ) -> None:
    """Sets the current Image's pixel data."""
    if CurrentImage:
        Pixels = getattr(Pixels, '__value__', Pixels )
        if Pixels.__class__ is str or hasattr(Pixels.__class__, '__iter__' ): CurrentImage.Pixels = Pixels
        else: print('ERROR: ugeSetImageData() expects an array of color/index data or an image file.')
    else: print('ERROR: ugeSetImageData() expected a defined image.')

@UGE_GLOBAL_WRAPPER
@register([
    CONST.UGE_MODEL_SCRIPT,
    CONST.UGE_IMAGE_SCRIPT,
    CONST.UGE_PALETTE_SCRIPT
    ])
def ugeSetImageColors(Colors: str or [vector] = [] ) -> None:
    """Sets the current Image's palette colors."""
    if CurrentImage:
        Colors = getattr(Colors, '__value__', Colors )
        if Colors.__class__ is str or hasattr(Colors.__class__, '__iter__' ): CurrentImage.Colors = Colors
        else: print('ERROR: ugeSetImagePalette() expects an array of color data or a palette file.')
    else: print('ERROR: ugeSetImagePalette() expected a defined image.')