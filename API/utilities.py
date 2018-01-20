# -*- coding: utf8 -*-
from __future__ import print_function
import _warnings
# Tcll - provided these for a more-readable level of efficiency (to be removed when ported to py3)
# NOTE: these require the class to compare with:
#intType=(int,long).__contains__
#numType=(int,long,float,complex).__contains__
#strType=(str,unicode).__contains__

#iterType = lambda value: hasattr(value,'__iter__')

#'''


def newmap(): # DEPRECATED
    """DEPRECATED"""
    _warnings.warn('causes infinite recursion with objects that rely on themselves in __hash__',DeprecationWarning)
    d = {}
    return d.get,d.__setitem__

def stop(end=True):
    if end: raise StopIteration
    return end

from colorsys import rgb_to_hls, hls_to_rgb
# usage: R,G,B,A = hashcolor( sys.modules['/UGE_Type_Names/'][FName] )
def hashcolor(name):
    col = hash(name.__str__())>>8
    #R,G,B = ((col>>16)&255)/255.,((col>>8)&255)/255.,(col&255)/255.
    #R,G,B = (col>>16)&255, (col>>8)&255, col&255
    H,L,S = rgb_to_hls((col>>16)&255, (col>>8)&255, col&255) # Tcll - I give up
    R,G,B = hls_to_rgb(H, min(max(L,127),204) ,.75 if S<.75 else S)
    return (int(R)<<16)|(int(G)<<8)|int(B)
'''
def hashcolor(name):
    col = hash(name.__str__())
    R,G,B = (col>>16)&255,(col>>8)&255,col&255
    factor = (R+G+B)/3
    if factor<96: #too dark
        fix = factor/2
        R+=fix;G+=fix;B+=fix
        if R>255: R-=96
        if G>255: G-=96
        if B>255: B-=96
    if factor>223: #too light
        fix = (255-factor)/2
        R-=fix;G-=fix;B-=fix
        if R<0: R+=223
        if G<0: G+=223
        if B<0: B+=223
    return (int(R)<<16)|(int(G)<<8)|int(B)
#'''

import sys,time
getTime = time.clock if sys.platform == "win32" else time.time
defTime = time.gmtime( 0 ) # what to subtract from the results
class timer(object):
    __slots__=['startTime']
    def __init__(this): this.startTime = getTime()
    def checkpoint(this): # adaptive smart time notification (actually speaks English)
        endTime = time.gmtime(getTime()-this.startTime)
        years = endTime.tm_year - defTime.tm_year
        months = endTime.tm_mon - defTime.tm_mon
        days = endTime.tm_mday - defTime.tm_mday
        hours = endTime.tm_hour
        minutes = endTime.tm_min
        seconds = endTime.tm_sec
        multi = (years+months+days+hours+minutes)>0
        print("Finished in%s%s%s%s%s%s." % (
            ' %s Year%s'%(years,'s'[:]) if years else '',
            ' %s Month%s'%(months,'s'[:months!=1]) if months else '',
            ' %s Day%s'%(days,'s'[:days!=1]) if days else '',
            ' %s Hour%s'%(hours,'s'[:hours!=1]) if hours else '',
            ' %s Minute%s'%(minutes,'s'[:minutes!=1]) if minutes else '',
            ' %s%s Second%s'%('and '[:4*multi],seconds,'s'[:seconds!=1])))  # TODO: 0.031 Seconds
        