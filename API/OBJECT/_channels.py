# -*- coding: utf-8 -*-

def private():
    new = object.new
    class UGEChannels(object):
        def __new__( cls ):
            ch = new(cls)
            def call(*items: [str,int,None]) -> UGEObject:
                """create a new or reference an existing collection."""
                if len(items) > 1:
                    channel, item, *other = items
                    item    = getattr(item,'__value__',item)
                else: channel, = items; item = ...
                channel = getattr(channel,'__value__',channel)
                
                channels = getchannels(ch)
                cl = channels.get(channel,None)
                if cl is None: cl = channels[channel] = UGECollection(Parent,Base,**kw)
                
                if item is not ...: return cl(item)
                return cl
            
            ch.__call__ = method(call,ch)
            return ch
        
    return UGEChannels


UGEChannels = private()
del private

def ChannelsProp( cls: object, attr: str ) -> function:
    """reassigns a collection verification property to an existing member_descriptor attribute"""
    dsc = cls.__dict__[attr]
    dscget = dsc.__get__
    def setter(obj, val) -> None: """verify and set a collection"""; dscget(obj,cls)[:] = val
    property( dscget, setter )
    return dsc.__set__