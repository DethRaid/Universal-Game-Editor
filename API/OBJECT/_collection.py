# -*- coding: utf-8 -*-

# noinspection PyShadowingNames
def private():
    """private namespace"""
    
    from . import UGEObject
    from ..utilities import getset
    from ..OBJECT import basehandlers
    
    privateRegistry = {}
    getprivate = privateRegistry.__getitem__ # WARNING: do not use in __repr__ of target class
    setprivate = privateRegistry.__setitem__
    class privateAttrs(object):
        """UGECollection private attributes"""
        __slots__ = [
            '__base__',
            '__basehandler__',
            '__baseparents__',
            '__objects__',
            '__items__',
            '__indices__',
            '__builtin__',
            ]
        
    getbase,        setbase         = getset( privateAttrs, '__base__',        privatize=False )
    gethandler,     sethandler      = getset( privateAttrs, '__basehandler__', privatize=False )
    getbaseparents, setbaseparents  = getset( privateAttrs, '__baseparents__', privatize=False )
    getobjects,     setobjects      = getset( privateAttrs, '__objects__',     privatize=False )
    getitems,       setitems        = getset( privateAttrs, '__items__',       privatize=False )
    getindices,     setindices      = getset( privateAttrs, '__indices__',     privatize=False )
    getbuiltin,     setbuiltin      = getset( privateAttrs, '__builtin__',     privatize=False )
    
    new = object.__new__
    class UGECollection(object):
        __slots__=[
            '__repr__',
            '__len__',
            '__iter__',
            '__contains__',
            'current',
            # heirarchical
            '__root__',
            '__parents__',
        ]
        def __new__(cls, Parent: UGEObject, Base: UGEObject, **kw):
            """a collection of specific UGEObject types which behaves similar to an ordered collections.defaultdict.
            
            Parameters:
                Parent : the UGEObject-type holding this collection (applied to <Base>.__parent__)
                Base : the UGEObject-type used in the collection"""
            cl = new(cls)
            pr = new(privateAttrs); setprivate(cl,pr)
            if Base.__class__ is UGECollection:
                bpr = getprivate(Base)
                setbase( pr, getbase(bpr) )
                baseparents = getbaseparents( bpr ); baseparents[Parent.__name__] = Parent
                setbaseparents( pr, baseparents     )
                sethandler(     pr, gethandler(bpr) )
                setobjects(     pr, getobjects(bpr) )
                setbuiltin(     pr, getbuiltin(bpr) )
                
                cl.__root__ = Base.__root__
                cl.__parents__ = parents = Base.__parents__ + [Base]
            else:
                setbase(        pr, Base )
                setbaseparents( pr, {Parent.__name__:Parent} if Parent else {} )
                sethandler(     pr, basehandlers[Base.__name__] )
                setobjects(     pr, {}   ) # { object:object } # hash > object: object = __objects__['Name']
                if '__builtin__' in kw:
                    setbuiltin( pr, kw['__builtin__'] )
                    __builtins__[cl.__builtin__] = None
                else: cl.__builtin__ = ''
                
                cl.__root__     = cl # for quick lookup (passed down)
                cl.__parents__  = () # for Base instance creation
            
            items = {} # { Object: Index, ... }
            setitems(   pr, items )
            setindices( pr, {} ) # { Index: Object, ... }
            setcurrent( cl, None )
            
            cl.__contains__ = items.__contains__
            cl.__len__      = items.__len__
            cl.__iter__     = items.__iter__
            
            basedict = getbase(pr).__dict__; iteritems = items.items
            showName = 'Name' in basedict; showIndex = 'Index' in basedict; showBoth = showName & showIndex
            cl.__repr__ = lambda: '<collection { %s } >'%( ', '.join( "%s%s%s: %s"%(
                repr(obj.Name) if showName else '', ' | '*showBoth, Index if showIndex else '', obj ) for obj,Index in iteritems() ) )
            
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
        
        def __call__(cl,*item):
            """create a new base instance in the root or this collection (unless existent),
            then link this instance to it without setting the current (unless linked).
            
            Usage:
            - <collection>(None): return current (default)
            - <collection>(int(Index) or "Name"): create or reference and return on channel 0"""
            
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
            
            base = cl.__base__; basedict = base.__dict__
            indexable = 'Index' in basedict
            
            itemType = item.__class__
            if itemType is int:
                if not indexable:
                    raise KeyError(item)
                elif item in indices: current = indices[item]; current.Index = item; return current
                else:
                    raise IndexError('collection index %sout of range.'%('on channel %s '%channel if cl.useChannels else ''))
            objects = cl.__objects__
            if item in objects:
                current = objects[item]
                if item not in items:
                    items[current] = Index = len(items) # link with collection
                    if indexable: current.Index = Index; indices[Index] = current
            else: # item not registered
                strtype = itemType is str
                if cl.__parents__ and (strtype or itemType is base): # create in parent and link here
                    current = cl.__parents__[-1](item)
                    Index = items[current] = len(items)
                    if indexable: indices[Index] = current
                elif strtype:
                    Index = len(items)
                    current = base(mappingproxy(getbaseparents(pr)),cl,item,Index)
                    items[current] = Index
                    if indexable: indices[Index] = current
                    objects[current] = current
                else:
                    raise TypeError('%s is not a supported item type.'%itemType.__name__)
            return current

        def __getitem__(cl,item: [str,int,None]) -> UGEObject:
            """create a new base item instance (unless existent) in the current or root collection,
            then link this collection to it (unless linked) and set it as the current item."""
            current = __call__(cl,item); setcurrent(cl, current); return current

        def __setitem__( cl, item: [str,int,None], value: object ):
            """create a new base instance in the root or this collection (unless existent),
            then link this instance to it (unless linked) and set it as current, and set it's value(s)."""
            current = cl.__getitem__(item)
            if current: current[:] = value
            elif item is None:
                raise TypeError('collection has no current item.')
            else:
                print('WARNING: collection item %s could not be set'%item)
    
    setglobal = __builtins__.__dict__.__setitem__
    setcurrent = UGECollection.current.__set__
    def setter(cl,val):
        setcurrent( cl, val )
        if cl.__builtin__: setglobal( cl.__builtin__, getattr(val,'proxy',val) )
    UGECollection.current = property( UGECollection.current.__get__, setter )
private()
del private

from ..OBJECT import properties
def CollectionProp( cls: object, attr: str, base: object, **kw ):
    """reassigns a collection verification property to an existing member_descriptor attribute"""
    name = cls.__name__; initializers = properties[name] = properties.get(name,set())
    dsc = cls.__dict__[attr]
    dscget = dsc.__get__; dscset = dsc.__set__
    def setter(obj, val) -> None: """verify and set a collection"""; dscget(obj,cls)[:] = val
    setattr(cls,attr,property( dscget, setter ))
    strbase = base.__class__ is str
    def init(obj: UGECollection):
        """Initializer"""
        # NOTE: obj.__owner__ is for UGEObject sub-type objects that link to the owning UGEObject (otherwize the owner is itself).
        own = getattr(obj,'__owner__',obj)
        dscset(obj, UGECollection( own, getattr(own.__parents__[base],attr) if strbase else base, **kw ))
    initializers.add(init)