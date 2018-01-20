# -*- coding: utf-8 -*-

from . import UGEObjectConstructor, new

class UGEChannels(object):
    pass

def ChannelsProp( cls: object, attr: str ) -> function:
    """reassigns a collection verification property to an existing member_descriptor attribute"""
    dsc = cls.__dict__[attr]
    dscget = dsc.__get__
    def setter(obj, val) -> None: """verify and set a collection"""; dscget(obj,cls)[:] = val
    property( dscget, setter )
    return dsc.__set__