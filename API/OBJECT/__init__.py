# -*- coding: utf-8 -*-
"""Heart of all UGEObject types"""

defined = set()
extensions = {}
class extension(object):
    """decorator to apply read-only properties to UGEObject sub-classes when defined."""
    __slots__ = ['ext']
    def __init__(this, applyto: str) -> None:
        if applyto in defined: print('WARNING: %s has already been defined, extensions cannot be applied.')
        if applyto in extensions: this.ext = extensions[applyto]
        else: this.ext = extensions[applyto] = {}
    def __call__(this, func: function): this.ext[func.__name__] = func

def private():
    """link Hierarchical properties with descriptors"""

    newType = type.__new__
    new = object.__new__
    class UGEObjectConstructor(type):
        """UGEObject metaclass"""
        __slots__ = []
        # noinspection PyUnresolvedReferences
        def __new__(meta, name: str, bases: tuple, NS: dict, **kw):
            if '__slots__' not in NS: NS['__slots__'] = []
            public = NS.get('__public__',{})
            NS['__slots__'].extend(attr for attr in public if attr not in NS)
            for n,f in extensions.get(name,{}).items(): NS[n]=property(f); public[n]={'w'}
            disabled = NS.get('__disabled__',set())
            cls = newType(meta, name, bases, NS)
            PNS={}
            # this creates prx->obj link attributes using __public__ (if available and not disabled) from each class in cls.__mro__
            for c in cls.__mro__:
                for attr,s in (c.__public__.items() if '__public__' in c.__dict__ else []):
                    if attr not in disabled: ref = getattr(cls,attr); PNS[attr] = property( # need getattr on this line to search through __mro__
                        ( lambda obj: getattr(ref.__get__(obj,cls),'proxy',cls) ) if 'p' in s else ref.__get_, ref.__set__ if 'w'in s else None )
                    # Tcll - believe it or not, ^ this (excluding getattr()) is actually faster on average (though less
                    # efficient (more CPU spikes)) than basic member descriptors by ~20ns)
        
            pcl = cls.__proxy__ = type('%s-proxy'%name,(object,),dict( PNS,
                __slots__=['__repr__','__eq__','__ne__','__hash__','__getattribute__','__setattr__'],
                __new__=cls.__newproxy__, __name__=property(lambda obj: obj.__name__), __class__=property() ))
            classprop.__init__(lambda obj: pcl)
            defined.add(name); return cls

    class UGEObject(object, metaclass=UGEObjectConstructor):
        """A base class to be inherited for UGE Object types
    
        Usage:
        class Object(UGEObject):
            '''full example in API.FORMAT._object'''
            __public__ = {'Viewport':{'w'}} # enable: 'p': obj.proxy, 'w': link.__set__
            __slots__ = ['Data']
            def __init__( Ob, *other ):
                Ob.Data=None
                Ob.Viewport=0"""
        __public__ = {  '__getitem__':set(),'__setitem__':set(),'__contains__':set(),'__iter__':set(),'__len__':set(),
            'Name':{'w'},'Index':set(),} # type: dict[str] -> set
        __slots__  = ['__name__','__holder__','__parents__','__proxy__','proxy']
        __repr__   = lambda obj:'<%s "%s" >'%(obj.__name__,obj.Name)
        __hash__   = lambda obj: hash(obj.Name)
        __eq__     = lambda obj,other: obj.Name==other or obj.proxy is other or obj is other
        __ne__     = lambda obj,other: obj.Name!=other and obj.proxy is not other and obj is not other

        def __new__(cls, parents: mappingproxy, holder: UGECollection, *args, **kw):
            if cls is UGEObject:
                raise TypeError('UGEObject cannot be created or initialized.')
            obj = new(cls)
            Name,Idx,*other = args+none3
            if Name.__class__ is int: Idx = Name; Name = None
    
            if useIndex: setIndex(obj,Idx)
            if useName: obj.Name = Name
    
            # initialize
            setparents( obj, parents )
            setholder( obj, holder )
            for initializer in properties.get(cls,set()): initializer(obj)
            if isinstance(cls,Hierarchical): setPa(obj,None); setCh(obj,None); setPr(obj,None); setNx(obj,None)

    setparents = UGEObject.__parents__.__set__
    UGEObject.__parents__ = property( UGEObject.__parents__.__get__ )
    setholder = UGEObject.__holder__.__set__
    UGEObject.__holder__ = property( UGEObject.__holder__.__get__ )

    class Hierarchical(object, metaclass=UGEObjectConstructor):
        """Hierarchical attributes"""
        __slots__ = ['Parent','Child','Prev','Next']
        def __new__(cls, parent: UGEObject, holder: UGEObject, *args, **kw):
            if cls is UGEObject:
                raise TypeError('UGEObject cannot be created or initialized.')
            obj = new(cls)
            Name,*other = args
            if len(other): Idx,*other = other
            if Name.__class__ is int: Idx = Name; Name = None
    
            if useIndex: setIndex(obj,Idx)
            if useName: obj.Name = Name
    
            # initialize
            setparent( obj, parent )
            setholder( obj, holder )
            for initializer in properties.get(cls,set()): initializer(obj)
            if isinstance(cls,Hierarchical): setPa(obj,None); setCh(obj,None); setPr(obj,None); setNx(obj,None)
    
    getPa = Hierarchical.Pa.__get__; setPa = Hierarchical.Pa.__set__
    getCh = Hierarchical.Ch.__get__; setCh = Hierarchical.Ch.__set__
    getPr = Hierarchical.Pr.__get__; setPr = Hierarchical.Pr.__set__
    getNx = Hierarchical.Nx.__get__; setNx = Hierarchical.Nx.__set__

    def Paset(obj,value: (str, UGEObject)):
        """set Parent"""
        cls = obj.__class__
        value = getattr(value, '__value__', value) # Object.Parent = string()() # from frontend
        ClearParent = value is None
        if ClearParent or value.__class__ in {str,cls,cls.__proxy__}:
            if obj!=value:
                Parent = getPa(obj,cls)
                if Parent: # pull from the current parent
                    setPa(obj,None); Prev = getPr(obj,cls); Next = getNx(obj,cls)
                    if getCh(Parent,cls) == obj: setCh(Parent,Next)
                    if Prev: setNx(Prev,Next); setPr(obj,None)
                    if Next: setPr(Next,Prev); setNx(obj,None)
                if not ClearParent: # assign to the new parent
                    NewParent = obj.__holder__(value); setPa(obj,NewParent)
                    if getCh(NewParent,cls) is None: setCh(NewParent,obj)
                    else: # iterate through the parent's children and "append" obj object to the last child's Next attribute
                        ParentChild = getCh(NewParent,cls)
                        while getNx(ParentChild,cls): ParentChild = getNx(ParentChild,cls)
                        setNx(ParentChild,obj); setPr(obj,ParentChild)
            else: print("ERROR: %s.Parent cannot apply itself as it's parent"%cls.__name__)
        else: print('ERROR: %s.Parent received an invalid value (%s)'%(cls.__name__,value))
    # noinspection PyPropertyAccess
    Hierarchical.Parent.__init__(getPa,Paset)
    
    def Chset(obj,value: (str, UGEObject)):
        """set Child"""
        cls = obj.__class__
        value = getattr(value, '__value__', value) # Object.Child = string()() # abstract
        ClearChild = value is None
        if ClearChild or value.__class__ in {str,cls,cls.__proxy__}: setCh(obj,None if ClearChild else obj.__holder__(value))
    # noinspection PyPropertyAccess
    Hierarchical.Child.__init__(getCh,Chset)
    
    def Prset(obj,value: (str, UGEObject)):
        """set Prev"""
        cls = obj.__class__.__name__
        value = getattr(value, '__value__', value) # Object.Parent = string()() # from frontend
        SetFirst = value==None
        if SetFirst or value.__class__ in {str,cls,cls.__proxy__}:
            Prev = getPr(obj,cls); Next = getNx(obj,cls)
            if SetFirst:
                # pull from iteration
                if Prev:
                    setNx(Prev,Next)
                    if Next: setPr(Next,Prev)
                    # find first and apply as Next
                    Parent = getPa(obj,cls)
                    if Parent: setNx(obj,getCh(Parent,cls)); setCh(Parent,obj)
                    else: # no Parent found, reverse-iterate until None.
                        First = Prev
                        while getPr(First,cls): First = getPr(First,cls) # TODO: figure out a single-reference method
                        setNx(obj,First); setPr(First,obj)
                    setPr(obj,None)
            else:
                if obj!=value:
                    if Prev!=value:
                        # pull from iteration
                        if Prev: setNx(Prev,Next)
                        if Next: setPr(Next,Prev)
                        # insert into iteration at new location
                        NewPrev = obj.__holder__(value); setPr(obj,NewPrev)
                        NewNext = getPr(NewPrev,cls); setNx(obj,NewNext)
                        setNx(NewPrev,obj)
                        if NewNext: setPr(NewNext,obj)
                else: print('ERROR: %s.Prev cannot apply itself as previous'%cls)
        else: print('ERROR: %s.Prev received an invalid value (%s)'%(cls,value))
    # noinspection PyPropertyAccess
    Hierarchical.Prev.__init__(getPr,Prset)
    
    def Nxset(obj,value: (str, UGEObject)):
        """set Next"""
        cls = obj.__class__
        value = getattr(value, '__value__', value) # Object.Next = string()() # abstract
        ClearNext = value is None
        if ClearNext or value.__class__ in {str,cls,cls.__proxy__}: setNx(obj,None if ClearNext else obj.__holder__(value))
    # noinspection PyPropertyAccess
    Hierarchical.Next.__init__(getNx,Nxset)
    
    return UGEObjectConstructor, UGEObject, Hierarchical

private()
del private

# noinspection PyUnresolvedReferences
from ._collection import UGECollection, CollectionProp
from ._channels import UGEChannels, ChannelsProp

def IntProp( cls: object, attr: str ) -> None:
    """reassigns an int verification property to an existing member_descriptor attribute"""
    name = cls.__name__
    dsc = cls.__dict__[attr]
    dscset = dsc.__set__
    def setter(obj,val) -> None:
        """verify and set an int"""
        val = getattr(val,'__value__',val)
        if val.__class__ in {str,int,float}: dscset(obj,int(val))
        else: print('ERROR: %s.%s received an invalid value (%s)'%(name,attr,val.__class__))
    cls.__dict__[attr] = property(dsc.__get__,setter)

def FloatProp( cls: object, attr: str ) -> None:
    """reassigns a float verification property to an existing member_descriptor attribute"""
    name = cls.__name__
    dsc = cls.__dict__[attr]
    dscset = dsc.__set__
    def setter(obj,val) -> None:
        """verify and set a float"""
        val = getattr(val,'__value__',val)
        if val.__class__ in {str,int,float}: dscset(obj,float(val))
        else: print('ERROR: %s.%s received an invalid value (%s)'%(name,attr,val.__class__))
    cls.__dict__[attr] = property(dsc.__get__,setter)