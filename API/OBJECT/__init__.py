# -*- coding: utf-8 -*-
"""Heart of all UGEObject types"""

defined = set()
extensions = {}
class extension(object):
    """decorator to apply read-only properties to UGEObject sub-classes when defined."""
    __slots__ = ['objname']
    def __init__(this, applyto: str):
        if applyto in defined: print('WARNING: %s has already been defined, extensions cannot be applied.')
        this.objname = applyto
        extensions[applyto] = extensions.get(applyto,{})
    def __call__(this, func: function): extensions[this.objname][func.__name__] = (func,)
    def setter(this, func: function): extensions[this.objname][func.__name__] += (func,)

def private():
    """private namespace"""
    
    from ..utilities import getset

    newType = type.__new__
    new = object.__new__
    class UGEObjectConstructor(type):
        """UGEObject metaclass"""
        __slots__ = []
        # noinspection PyUnresolvedReferences
        def __new__(meta, name: str, bases: tuple, NS: dict, **kw):
            slots = NS['__slots__'] = set(NS.get('__slots__',set())).union({'Name','Index'}).difference(NS.get('__disabled__',set()))
            for n,funcs in extensions.get(name,{}).items(): NS[n]=property(*funcs)
            
            ugeobj = newType(meta, name, bases, NS) # TODO: mappingproxy(NS))
            if 'Name' in slots: properties[name]['Name'] = ugeobj.Name.__set__
            if 'Index' in slots: # NOTE: Index is relative to the root collection of this object
                properties[name]['Index'] = ugeobj.Index.__set__
                ugeobj.Index = property(ugeobj.Index.__get__,)
            defined.add(name); return ugeobj

    class UGEObject(object, metaclass=UGEObjectConstructor):
        """A base class to be inherited for UGE Object types
    
        Usage:
        class Object(UGEObject):
            '''full examples among API.FORMAT'''
            __slots__ = ['Data','Viewport']
            def __new__(cls, *other: tuple, **kw ):
                Ob=newUGEObject(cls,*other)
                Ob.Data=None
                Ob.Viewport=0
                return Ob"""
        #__public__ = {  '__getitem__':set(),'__setitem__':set(),'__contains__':set(),'__iter__':set(),'__len__':set()}
        __slots__  = ['__holder__','__parents__', 'Name','Index']
        __repr__   = lambda obj:'<%s "%s" >'%(obj.__name__,obj.Name)
        __hash__   = lambda obj: hash(obj.Name)
        __eq__     = lambda obj,other: obj.Name==other or obj.proxy is other or obj is other
        __ne__     = lambda obj,other: obj.Name!=other and obj.proxy is not other and obj is not other

        def __new__(cls, parents: mappingproxy, holder: UGECollection, *args, **kw):
            if cls is UGEObject:
                raise TypeError('UGEObject cannot be created or initialized.')
            obj = new(cls)
            Name,*other = args
            if len(other): Idx,*other = other
            if Name.__class__ is int: Idx = Name; Name = None
            
            # initialize
            setparents( obj, parents ); setholder( obj, holder )
            for name,initializer in properties.get(cls,{}).items():
                if name=='Name': initializer(obj,Name)
                if name=='Index': initializer(obj,Idx)
                else: initializer(obj)

    setparents = UGEObject.__parents__.__set__
    UGEObject.__parents__ = property( UGEObject.__parents__.__get__ )
    setholder = UGEObject.__holder__.__set__
    UGEObject.__holder__ = property( UGEObject.__holder__.__get__ )

    class Hierarchical(object, metaclass=UGEObjectConstructor):
        """Hierarchical attributes"""
        __slots__ = ['__holder__','__parents__', 'Name','Index','Parent','Child','Prev','Next']
        def __new__(cls, parents: mappingproxy, holder: UGECollection, *args, **kw):
            if cls is UGEObject:
                raise TypeError('UGEObject cannot be created or initialized.')
            obj = new(cls)
            Name,*other = args
            if len(other): Idx,*other = other
            if Name.__class__ is int: Idx = Name; Name = None
    
            # initialize
            sethparents( obj, parents ); sethholder( obj, holder )
            setPa(obj,None); setCh(obj,None); setPr(obj,None); setNx(obj,None)
            for name,initializer in properties.get(cls,{}).items():
                if name=='Name': initializer(obj,Name)
                if name=='Index': initializer(obj,Idx)
                else: initializer(obj)

    sethparents = Hierarchical.__parents__.__set__
    Hierarchical.__parents__ = property( Hierarchical.__parents__.__get__ )
    sethholder = Hierarchical.__holder__.__set__
    Hierarchical.__holder__ = property( Hierarchical.__holder__.__get__ )
    
    getPa, setPa = getset( Hierarchical, 'Parent', privatize=False )
    getCh, setCh = getset( Hierarchical, 'Child',  privatize=False )
    getPr, setPr = getset( Hierarchical, 'Prev',   privatize=False )
    getNx, setNx = getset( Hierarchical, 'Next',   privatize=False )

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
    Hierarchical.Parent = property(getPa,Paset)
    
    def Chset(obj,value: (str, UGEObject)):
        """set Child"""
        cls = obj.__class__
        value = getattr(value, '__value__', value) # Object.Child = string()() # abstract
        ClearChild = value is None
        if ClearChild or value.__class__ in {str,cls,cls.__proxy__}: setCh(obj,None if ClearChild else obj.__holder__(value))
    Hierarchical.Child = property(getCh,Chset)
    
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
    Hierarchical.Prev = property(getPr,Prset)
    
    def Nxset(obj,value: (str, UGEObject)):
        """set Next"""
        cls = obj.__class__
        value = getattr(value, '__value__', value) # Object.Next = string()() # abstract
        ClearNext = value is None
        if ClearNext or value.__class__ in {str,cls,cls.__proxy__}: setNx(obj,None if ClearNext else obj.__holder__(value))
    Hierarchical.Next = property(getNx,Nxset)
    
    return UGEObjectConstructor, UGEObject, Hierarchical

properties = {} # { class_name: { attr: initializer } }
basehandlers = {} # { class_name: { handler } }

UGEObjectConstructor, UGEObject, Hierarchical = private()
del private

newUGEObject = UGEObject.__new__

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