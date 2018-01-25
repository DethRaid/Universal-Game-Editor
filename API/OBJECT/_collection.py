# -*- coding: utf-8 -*-

from . import UGEObjectConstructor, new
from ..utilities import stop

def newitem(cl, *args,**kw):
    return

def setitem(this,item,value,channel=0):
    """create a new base instance in the root or this collection (unless existent),
    then link this instance to it (unless linked) and set it's current.
    
    Usage:
    - <collection>[None] = value: change the current item
    - <collection>[int() if useIDs else "Name"] = value: create or reference and return on channel 0
    - <collection>[*above*, 1] = value (if useChannels): operate on channel 1
    - <collection>[*above*, "Name"] = value (if namedChannels): operate on channel "Name" """
    
    if hasattr(item,'__value__'): item=item.__value__
    if item is None:
        if this.current is None:
            raise TypeError('collection has no current item.')
        item = this.current.Name
    
    indices = this.indices
    itemHash = hash(item)
    itemType = item.__class__
    if itemType is tuple:
        item, channel = item
        
        if hasattr(channel,'__value__'): channel=channel.__value__
        channelType = channel.__class__
        if not this.useChannels and channel!=0: print('WARNING: using channels on a non-channeled collection.')
        if not this.namedChannels and channelType is str:
            raise TypeError('named channels are not supported in this collection.')
        elif not (channelType is int or channelType is str):
            raise TypeError('%s is not a valid channel type.'%channelType.__name__)
        
        # since item has changed:
        if hasattr(item,'__value__'): item=item.__value__
        itemHash = hash(item)
        itemType = item.__class__
    
    # bring the itemHashes out of the channel for fast access
    channels = this.channels
    if channel in channels: items = channels[channel]
    else: items = channels[channel] = set()
    
    idx = indices.get(itemHash,None)
    if idx is None: # item not registered
        base = this.Base
        if itemType is (int if this.useIDs else str) or base.__name__ in itemType.__name__:
            parents = this.parents
            if parents: # get current from parent
                parent = parents[-1]
                backup = parent.__parent__
                parent.__parent__ = this.__parent__ # pass the containing UGEObject up the hierarchy before initializing the base.
                this.current = current = parent(item,channel) # get current from parent
                parent.__parent__ = backup
                items.add(itemHash)
            else:
                objects = this.objects
                indices[itemHash] = len(objects)
                this.current = current = base(item)
                current.__holder__ = this # reverse-link for hierarchical validation (search this collection)
                items.add(itemHash)
                objects.append(current)
        else:
            raise TypeError('%s is not a supported item type.'%itemType.__name__)
    else:
        if itemHash not in items: items.add(itemHash)
        this.current = current = this.objects[idx]
    current.__item__ = value
    
# noinspection PyUnboundLocalVariable,PyArgumentList
class UGECollection(object, metaclass=UGEObjectConstructor ):
    __slots__=[
        '__len__',
        '__contains__',
        '__setitem__',
        '__iter__', 
        'proxy',
        #'useChannels',
        #'namedChannels',
        '__base__',
        '__parent__',
        '__root__',
        '__objects__',
        '__indices__',
        '__inheritors__',
        '__parents__',
        #'__channels__'
        '__builtin__'
    ]
    __public__ = {'current':{'p'},'new':{'p'},'__setitem__':set()}
    __disabled__ = {'Name','Index'}

    # noinspection PyUnresolvedReferences
    def __newproxy__(cls,obj):
        prx=new(cls)
        
        orepr = obj.__repr__
        cls.__repr__.__set__(prx, lambda:'<%s>'%orepr() )
        
        ohash = obj.__hash__
        cls.__hash__.__set__(prx, lambda:ohash() )
        
        ogetitem = obj.__getitem__
        def getitem(prx, item):
            if item.__class__==tuple:
                if len(item)==1: return (I.proxy for I in ogetitem(item))
                elif item[1] is None: return ogetitem(item)
            return ogetitem(item).proxy
        cls.__getitem__.__set__(prx, getitem )
        
        oiter = obj.__iter__
        cls.__iter__.__set__(prx, lambda:(item.proxy for item in oiter()) )
        
        ocall = obj.__call__
        cls.__call__.__set__(prx, lambda *item: ocall(item) if len(item)>1 and item[1] is None else ocall(item).proxy )
        '''
        def items(prx):
            src=GetRawObject(prx); objects=src.objects; indices=src.indices
            return ((ch, (objects[indices[h]].proxy for h in items)) for ch,items in src.channels.items())
        '''
        PNS = cls.__dict__.__getitem__
        ocl = obj.__class__
        cls.__getattribute__.__set__(prx, lambda attr: PNS(attr).__get__(obj,ocl))
        cls.__setattr__.__set__(prx, lambda attr, val: PNS(attr).__set__(obj,val))
        return prx
    
    def __new__(cls, Parent, Base, channels=False, named=False, **kw):
        """
        a (optionally channeled) collection of specific Object types which behaves similar
        to a collections.defaultdict in that it automatically creates a non-existent Object.
        
        Parameters:
            Parent : the Object-type holding this collection (applied to <Base>.__parent__)
            Base : the Object-type used by the collection 
            channels : use extra numbers to index a sub-array of objects (defaults to False) (ignored if inherited)
            named : use extended channel support for both names and numbers (defaults to False) (ignored if inherited)
        
        example usage:
        
            Objects = collection(None, Object, channels=True)
            
            obj0 = Objects[ 'Object0' ] # create "Object0" on channel 0
            Objects[ 'Object0', 1 ] # reference "Object0" and link on channel 1
        """
        cl = new(cls)
        # TODO: use less attributes (decrease complexity and memory use, and increase performance)
        if Base.__class__ is UGECollection:
            cl.useChannels = Base.useChannels
            cl.namedChannels = Base.namedChannels
            
            cl.__base__ = base = Base.__base__
            cl.__objects__ = objects = Base.__objects__
            
            cl.__root__ = Base.__root__
            cl.__parents__ = parents = Base.__parents__ + [Base]
            cl.__inheritors__ = inheritors = Base.__inheritors__
            for parent in parents: inheritors[parent].append(cl)

            cl.__builtin__ = Base.__builtin__
            
        else:
            cl.useChannels = channels
            cl.namedChannels = named
            
            cl.__base__ = base = Base
            cl.__objects__ = objects = {} # { object:object } # hash > object: object = __objects__['Name']
            
            cl.__root__ = cl # for quick lookup (passed down)
            cl.__parents__ = [] # for object addition and inheritor application
            cl.__inheritors__ = inheritors = {} # { this: [ <collection>, ... ] } # for object removal

            if '__builtin__' in kw:
                cl.__builtin__ = kw['__builtin__']
                __builtins__.__dict__[cl.__builtin__] = None
            else: cl.__builtin__ = ''
        
        #disabled = getattr(base,'__disabled__',set()).__contains__
        
        cl.current=None
        cl.__channels__ = channels = {} # { channel: ({ object: Index, ... }, { Index: object, ... }) }
        inheritors[cl] = [cl]
        cl.__parent__ = Parent
        
        cl.__iter__ = channels.__iter__ if cl.useChannels else lambda: iter(channels[0][0])
        if hasattr(base, '__item__'): cl.__setitem__ = setitem

        pcl = cls.__proxy__
        prx = cl.proxy = cls.__proxy__(cl)
        #prx.len = lambda cls,channel=0: len(channels.get(channel,[]))
        olen = cl.__len__ = channels.__len__
        pcl.__len__.__set__(prx, lambda:olen() )
        ocont = cl.__contains__ = objects.__contains__
        pcl.__contains__.__set__(prx, lambda other:ocont(other) )

        cls.new.__set__(cl,method(newitem,cl) if hasattr(base,'new') else cl.__call__)

        return cl

    def new(cl, item: [str,int,dict]) -> UGEObject:
        """create a new base item instance (unless existent) in the current or root collection,
        then link this collection to it (unless linked) and set it as the current item."""
    
        item = getattr(item,'__value__',item)
        itemType = item.__class__
        strtype = itemType is str
        inttype = itemType is int
    
        base = getbase(cl)
        basedict = base.__dict__
        nameable = 'Name' in basedict
        indexable = 'Index' in basedict
        if (strtype and nameable) or (inttype and indexable): return cl.__getitem__(item) # TODO: pull processing here (boost performance)
        else:
            if inttype:
                raise KeyError(item)
            if strtype:
                raise TypeError('collection indices must be integers, not str')
            items   = getitems(cl)
            indices = getindices(cl)
            objects = getobjects(cl)
            Index   = len(items)
            handler = gethandler(cl)
            current = handler(mappingproxy(getbaseparents(cl)),cl,item,Index) if handler else\
                base(mappingproxy(getbaseparents(cl)),cl,item,Index)
            items[current] = Index
            if indexable: indices[Index] = current
            objects[current] = current
        
            return current
        
    def __repr__(this):
        disabled = getattr(this.__base__,'__disabled__',set()).__contains__
        showName = not disabled('Name'); showIndex = not disabled('Index'); both = showName and showIndex
        return '<collection %s >'%( ', '.join( ('%s: { %s }' if this.useChannels else '%s{ %s }')%(
            repr(channel) if this.useChannels else '', ', '.join( "%s%s%s: %s"%(
                repr(obj.Name) if showName else '', ' | '*both, Index if showIndex else '', obj
            ) for obj,Index in items.items() )
        ) for channel,(items,indices) in this.__channels__.items() ) )
    
    def __call__(cl,*item):
        """create a new base instance in the root or this collection (unless existent),
        then link this instance to it without setting the current (unless linked).
        
        Usage:
        - <collection>(None): return current (default)
        - <collection>(int(Index) or "Name"): create or reference and return on channel 0
        - <collection>(*above*, 1) if useChannels: operate on channel 1
        - <collection>(*above*, "Name") if namedChannels: operate on channel "Name"
        - <collection>(int()/"Name", None): return the channels the specified item is in"""
        
        if not item: item=(None,)
        # untuple:
        if len(item)==2: item,channel = item
        else: item = item[0]; channel = 0
        
        if hasattr(channel,'__value__'): channel=channel.__value__
        channelType = channel.__class__
        if not cl.useChannels and channel!=0: print('WARNING: using channels on a non-channeled collection.')
        if not cl.namedChannels and channelType is str:
            raise TypeError('named channels are not supported in this collection.')
        elif not (channelType is int or channelType is str):
            raise TypeError('%s is not a valid channel type.'%channelType.__name__)
        
        if hasattr(item,'__value__'): item=item.__value__
        if item is None: return cl.current
        if channel is None: return (channel for channel,items in cl.__channels__.items() if item in items)
        
        # bring the items and indices out of the channel for fast access
        channels = cl.__channels__
        if channel in channels: items,indices = channels[channel]
        else: items,indices = channels[channel] = ({},{})
        
        base = cl.__base__
        disabled = getattr(base,'__disabled__',set()).__contains__
        doIndex = not disabled('Index')
        
        itemType = item.__class__
        if itemType is int:
            if not doIndex:
                raise KeyError(item)
            elif item in indices: current = indices[item]; current.Index = item; return current
            else:
                raise IndexError('collection index %sout of range.'%('on channel %s '%channel if cl.useChannels else ''))
        objects = cl.__objects__
        if item in objects:
            current = objects[item]
            if item not in items:
                items[current] = Index = len(items) # link with collection
                if doIndex: current.Index = Index; indices[Index] = current
        else: # item not registered
            strtype = itemType is str
            if cl.__parents__ and (strtype or itemType.__name__ == base.__name__): # create in parent and link here
                current = cl.__parents__[-1](item,channel)
                items[current] = Index = len(items)
                if doIndex: current.Index = Index; indices[Index] = current
            elif strtype:
                if disabled('Name'):
                    raise TypeError('collection items %smust be integers, not %s'%('for channel %s '%channel if cl.useChannels else '',base.__name__))
                Index = len(items)
                if doIndex:
                    current = base(cl.__parent__,item,Index)
                    items[current] = Index; indices[Index] = current
                else: current = base(cl.__parent__,item); items[current] = Index
                current.__holder__ = cl # reverse-link for hierarchical validation (search this collection)
                objects[current] = current
            else:
                raise TypeError('%s is not a supported item type.'%itemType.__name__)
        return current
        
    def __getitem__(cl,item,channel=0):
        """create a new base instance in the root or this collection (unless existent),
        then link this instance to it (unless linked) and set it's current.
        
        Usage:
        - <collection>[None]: return current
        - <collection>[int(Index) or "Name"]: create or reference and return on channel 0
        - <collection>[*above*, 1] if useChannels: operate on channel 1
        - <collection>[*above*, "Name"] if namedChannels: operate on channel "Name"
        - <collection>[int(Index)/"Name", None]: return the channels the specified item is in
        - <collection>[channel,] if useChannels: iterate over the items in the channel"""
        
        if hasattr(item,'__value__'): item=item.__value__
        if item is None: return cl.current
        itemType = item.__class__
        if itemType is tuple:
            iterate = len(item)==1 # iterate over items in this channel
            if iterate: channel = item[0]
            else: item, channel = item
            
            if hasattr(channel,'__value__'): channel=channel.__value__
            channelType = channel.__class__
            if not cl.useChannels and channel!=0: print('WARNING: using channels on a non-channeled collection.')
            if not cl.namedChannels and channelType is str:
                raise TypeError('named channels are not supported in this collection.')
            elif not (channelType is int or channelType is str):
                raise TypeError('%s is not a valid channel type.'%channelType.__name__)
            if iterate: return iter(cl.__channels__.get(channel,({},{}))[0])
            
            # since item and channel have changed:
            if hasattr(item,'__value__'): item=item.__value__
            if channel is None: return (channel for channel,(items,indices) in cl.__channels__.items() if item in items)
            itemType = item.__class__
        
        # bring the item hashes and indices out of the channel for fast access
        channels = cl.__channels__
        if channel in channels: items,indices = channels[channel]
        else: items,indices = channels[channel] = ({},{})
        
        base = cl.__base__
        disabled = getattr(base,'__disabled__',set()).__contains__
        doIndex = not disabled('Index')
        if itemType is int:
            if not doIndex:
                raise KeyError(item)
            elif item in indices: cl.current = current = indices[item]; current.Index = item; return current
            else:
                raise IndexError('collection index %sout of range.'%('on channel %s '%channel if cl.useChannels else ''))
        objects = cl.__objects__
        if item in objects:
            cl.current = current = objects[item]
            if item not in items:
                items[current] = Index = len(items) # link with collection
                if doIndex: current.Index = Index; indices[Index] = current
        else: # item not registered
            strtype = itemType is str
            if cl.__parents__ and (strtype or itemType.__name__ == base.__name__): # create in parent and link here
                cl.current = current = cl.__parents__[-1](item,channel)
                items[current] = Index = len(items)
                if doIndex: current.Index = Index; indices[Index] = current
            elif strtype:
                if disabled('Name'):
                    raise TypeError('collection items %smust be integers, not %s'%('for channel %s '%channel if cl.useChannels else '',base.__name__))
                Index = len(items)
                if doIndex:
                    cl.current = current = base(cl.__parent__,item,Index)
                    items[current] = Index; indices[Index] = current
                else: cl.current = current = base(cl.__parent__,item); items[current] = Index
                current.__holder__ = cl # reverse-link for hierarchical validation (search this collection)
                objects[current] = current
            else:
                raise TypeError('%s is not a supported item type.'%itemType.__name__)
        return current

# noinspection PyUnresolvedReferences
def private():
    setglobal = __builtins__.__dict__.__setitem__
    setcurrent = UGECollection.current.__set__
    def setter(cl,val):
        setcurrent( cl, val )
        if cl.__builtin__: setglobal( cl.__builtin__, getattr(val,'proxy',val) )
    UGECollection.current = property( UGECollection.current.__get__, setter )
private()
del private

def CollectionProp( cls: object, attr: str ) -> function:
    """reassigns a collection verification property to an existing member_descriptor attribute"""
    dsc = cls.__dict__[attr]
    dscget = dsc.__get__
    def setter(obj, val) -> None: """verify and set a collection"""; dscget(obj,cls)[:] = val
    property( dscget, setter )
    return dsc.__set__