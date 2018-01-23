
from SIDE.common import *


def repaint(this): this.viewport().repaint(); return

def setFont(this, f):
    # recalculate all of our metrics/offsets
    fm = QtGui.QFontMetrics(f)
    this.font_width  = fm.width('X')
    this.font_height = fm.height()
    QtGui.QAbstractScrollArea.setFont(this,f)
    return

def updateScrollbar(this):
    this.verticalScrollBar().setMaximum( len(this.data) )
    return

class Types(QtGui.QAbstractScrollArea):

    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        this.parent = parent

        this.data = []

        new_dict = {}
        for k,v in ugeTypes.items():
            if v in new_dict: new_dict[v].append(k)
            else: new_dict[v] = [k]

        for v in sorted(new_dict):
            color = text2color(v)
            for f in sorted(new_dict[v]):
                this.data.append((f,color))

        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 8))
        this.updateScrollbar()
        this._painter = QtGui.QPainter()

    repaint = repaint
    setFont = setFont
    updateScrollbar = updateScrollbar

    def paintEvent(this, event):

        painter = this._painter
        painter.begin(this.viewport())

        startPos = this.verticalScrollBar().value()
        painter.translate(0, -startPos*this.font_height) # set scroll position
        
        for I,(T,C) in enumerate(this.data):
            x,y,w,h = 5, I*this.font_height, this.font_width*len(T), this.font_height
            painter.fillRect( x,y,w,h, C)
            painter.drawText( x,y,w,h, Qt.AlignTop, QtCore.QString(T) )
            
        painter.end()


class Functions(QtGui.QAbstractScrollArea):

    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        this.parent = parent

        this.data = list(sorted(ugeFuncs.keys()))
        this.bfcolor = ugeBFuncsClr
        this.fcolor = ugeFuncsClr

        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 8))
        this.updateScrollbar()
        this._painter = QtGui.QPainter()

    repaint = repaint
    setFont = setFont
    updateScrollbar = updateScrollbar
    
    def paintEvent(this, event):
        painter = this._painter
        painter.begin(this.viewport())

        startPos = this.verticalScrollBar().value()
        painter.translate(0, -startPos*this.font_height) # set scroll position
        
        for I,F in enumerate(this.data):
            x,y,w,h = 5, I*this.font_height, this.font_width*len(F), this.font_height
            painter.setPen( this.bfcolor if F.startswith('uge') else this.fcolor )
            painter.drawText( x,y,w,h, Qt.AlignTop, QtCore.QString(F) )
            
        painter.end()


class Constants(QtGui.QAbstractScrollArea):

    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        this.parent = parent
        
        categories = { C.__class__.__name__:[] for C in ugeConst.values() }
        for c,C in ugeConst.items(): categories[C.__class__.__name__].append(c)
            
        this.data = [c for N in sorted(categories) for c in categories[N]]
        this.color = ugeConstClr
        
        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 8))
        this.updateScrollbar()
        this._painter = QtGui.QPainter()

    repaint = repaint
    setFont = setFont
    updateScrollbar = updateScrollbar

    def paintEvent(this, event):
        painter = this._painter
        painter.begin(this.viewport())

        startPos = this.verticalScrollBar().value()
        painter.translate(0, -startPos*this.font_height) # set scroll position
        
        for I,C in enumerate(this.data):
            x,y,w,h = 5, I*this.font_height, this.font_width*len(C), this.font_height
            painter.setPen( this.color )
            painter.drawText( x,y,w,h, Qt.AlignTop, QtCore.QString(C) )
            
        painter.end()
        return
