# -*- coding: utf-8 -*-

# noinspection PyShadowingNames
def private():
    """private namespace"""
    
    from . import UGEObject, UGECollection
    from ..OBJECT import properties
    
    new = object.new
    class UGEChannels(object):
        def __new__(cls, Parent: UGEObject, Base: UGEObject, **kw):
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

    def ChannelsProp( cls: object, attr: str, base: object, **kw ):
        """reassigns a channel verification property to an existing member_descriptor attribute"""
        name = cls.__name__; initializers = properties[name] = properties.get(name,set())
        dsc = cls.__dict__[attr]
        dscget = dsc.__get__; dscset = dsc.__set__
        def setter(obj, val) -> None: """verify and set a collection"""; dscget(obj,cls)[:] = val
        setattr(cls,attr,property( dscget, setter ))
        strbase = base.__class__ is str
        def init(obj):
            """called when the owning class is instantiated"""
            # NOTE: obj.__owner__ is for UGEObject sub-type objects to link back to the owner when referenced from (otherwize the owner is itself).
            own = getattr(obj,'__owner__',obj)
            dscset(obj, UGEChannels( own, getattr(own.__parents__[base],attr) if strbase else base, **kw ))
        initializers.add(init)
        
    return UGEChannels, ChannelsProp


UGEChannels, ChannelsProp = private()
del private