# -*- coding: utf8 -*-
from __future__ import print_function

from sys import modules
from . import register, FILE

UGE_GLOBAL_WRAPPER = modules[ '/UGE_GLOBAL_WRAPPER/' ]  # moddable API wrapper

setglob = modules.__setitem__
@register( all )
class switch( object ):
    """Logic object to test a value against various cases.

    usage:
    - switch( test_value )
    - enum_struct = switch( data_struct, [ data_struct ] )
    - enum_struct = switch( data_struct, { case_value: data_struct } )"""
    __slots__ = [ 'value', 'case', '__addr__', '__size__', '__value__', '__dereferenced__' ]
    __name__ = 'switch'  # get name from instance rather than class
    __color__ = 0xFFFFFF

    def __init__( this, value, cases=None ):
        if cases:
            this.__dereferenced__ = False
            this.value = value
            this.case = cases.__getitem__
            return
        setglob( '/UGE_SWITCH_VALUE/', value )

    @UGE_GLOBAL_WRAPPER
    def __call__( this, value=None, label='', *args, **kwargs ):
        cf = FILE._current
        this.__addr__ = cf.offset
        this.__value__ = v = this.case( this.value( value, label=label ) )()
        this.__size__ = cf.offset
        FILE._current._register_instance( this )
        return v

getglob = modules.__getitem__
@UGE_GLOBAL_WRAPPER
@register( all )
def case( *comparators ):
    """Logic function to test against a switch value.

    usage:
    - if case( comparator[, comparator[, ...]] ):"""
    return getglob( '/UGE_SWITCH_VALUE/' ) in comparators
