
from SIDE.common import *

class Functions(QtGui.QAbstractScrollArea):

    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        this.parent = parent

        this.data = [k for k in ugeFuncs]
        this.funcColor = ugeFuncsClr

        # default to a simple monospace font
        this.setFont(QtGui.QFont("Courier New", 8))
        this.updateScrollbar()
        this._painter = QtGui.QPainter()

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

    def paintEvent(this, event):

        painter = this._painter
        painter.begin(this.viewport())

        startPos = this.verticalScrollBar().value()
        painter.translate(0, -startPos*this.font_height) # set scroll position
        
        for I,F in enumerate(this.data):
            x,y,w,h = 5, I*this.font_height, this.font_width*len(F), this.font_height
            painter.setPen( this.funcColor )
            painter.drawText( x,y,w,h, Qt.AlignTop, QtCore.QString(F) )
            
        painter.end()
 
        return
