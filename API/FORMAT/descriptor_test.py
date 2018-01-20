
class ObjectProp(object):
    __slots__ = ['__map__','__set__']
    __get__ = lambda dsc, obj, objcls=None: dsc if obj is None else dsc.__map__[obj]
    def __init__(dsc): dsc.__map__={}
    def setter(dsc,func):
        func.__defaults__ = (dsc,None,None)
        dsc.__set__ = func
        return dsc

class test(object):
    __slots__ = []

    prop = ObjectProp()
    @prop.setter
    def prop(dsc,this,value): print((dsc,this,value))


i = test()
i.prop=15
