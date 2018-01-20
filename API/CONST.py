# -*- coding: utf8 -*-

# this module is used to define UGE constants under it's namespace.
# originally this module was designed to follow an old C-programming standard
# which defines all needed constants within 1 file or module and references them locally from it.

# Tcll - I find it better to organize code via categorized sections.
# so we define the constants within those sections, however we reference them from this namespace.
# this makes it easier to control which constants go to which script-type-namespaces,
# while also allowing us to reference them like so:

class UGE_CONSTANT(object):
    '''base class for UGE constants.'''
    def __init__(this,name):
        this.__name__ = name

def define( constants, Type, scopes=[] ):
    for c in constants:
        C = globals()[c] = Type(c)
        for scope in scopes: scope.NS[c] = C