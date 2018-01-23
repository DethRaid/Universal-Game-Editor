
from SIDE.common import *

# node format: [ dt, assignment, label, level, skip, expanded, code_line ]
# level = len parents
# skip = len children
# expanded = None: no toggle; True: don't skip anything; False: skip children
    
class TreeView(QtGui.QAbstractScrollArea):
    # NOTE: this is a, badly designed, pseudo tree viewer class, in-depth processing is not performed. (only what's needed is drawn)
    
    def __init__(this, parent = None):
        QtGui.QAbstractScrollArea.__init__(this, parent)
        
        # colors
        this.textColor      = QtGui.QColor(  0,   0,   0, 255)

        this.headerColor    = QtGui.QColor(0xE0,0xE0,0xE0, 255)
        this.lineColor      = QtGui.QColor(192, 192, 192, 255)
        this.treeLineColor  = QtGui.QColor( 96,  96,  96, 255)
        this.labelColor     = QtGui.QColor(  0, 0xA0,   0, 255)
        
        this.grayRow        = QtGui.QColor(0xF6,0xF6,0xF6, 255)
        this.white          = QtGui.QColor(255, 255, 255, 255)

        #this.Y = 0
        
        this.widget_height = this.height() # in pixels
        this.widget_width = this.width() # in pixels

        this.TextStartX = 0
        this.TextStartY = 0
        this.TextEndX = 0
        this.TextEndY = 0
        
        this.numLines = 0
        this.textWidth = 0
        
        this.rows = []
        this.collapsed = {} # { node_index: node_children, ... }

        this.selections = [None]
        this.onselect = lambda this: None
        this.ondeselect = lambda this: None

        # quick QString display list for drawing ASCII text
        #this._Q_char_table = { chr(c): QtCore.QString(chr(c)) for c in xrange(256)}
        this.setFont(QtGui.QFont("Courier New", 8)) # default to a simple monospace font

        this._painter = QtGui.QPainter()

        this.offlen = 8
        this.offset_column = 12*this.font_width
        this.size_column = 8*this.font_width
        this.data_column = 18*this.font_width
        this.value_column = 18*this.font_width

    def repaint(this): this.viewport().repaint()

    def setFont(this, f):
        # recalculate all of our metrics/offsets
        fm = QtGui.QFontMetrics(f)
        this.font_width  = fm.width('X')
        this.font_height = fm.height()
        #this.updateScrollbars()
        # TODO: assert that we are using a fixed font & find out if we care?
        QtGui.QAbstractScrollArea.setFont(this,f)
        return
    
    def updateScrollbars(this):
        num_rows = this.rows.__len__()
        max_rows = (this.height()/this.font_height)
        max_cols = (this.width()/this.font_width)
        this.verticalScrollBar().setMaximum( num_rows-max_rows if num_rows>max_rows else 0 )
        #this.horizontalScrollBar().setMaximum( this.textWidth-max_cols if this.textWidth>max_cols else 0 )
        this.horizontalScrollBar().setMaximum( 0 )
        return

    '''
    on to the events:
    '''
    def drawToggle(this,_X,_Y,x,y,X,Y,D,Ex):
        this._painter.fillRect( x,y,D,D, this.white )
        this._painter.drawLine(x,y,X,y)
        this._painter.drawLine(X,y,X,Y)
        this._painter.drawLine(x,Y,X,Y)
        this._painter.drawLine(x,y,x,Y)
        
        this._painter.drawLine(x+2,_Y,X-2,_Y)
        if not Ex: this._painter.drawLine(_X,y+2,_X,Y-2)

    #def skip(this,children): return len(children)+sum(this.skip(child.children) for child in children)

    def paintEvent(this, event):
        painter = this._painter
        painter.begin(this.viewport())
        
        this.TextStartX = this.horizontalScrollBar().value()
        StartY = this.TextStartY = this.verticalScrollBar().value()
        this.widget_height = this.height() # in pixels
        this.widget_width = this.width() # in pixels
        W,H = this.font_width,this.font_height
        W2 = W*2
        
        painter.translate( -this.TextStartX * W, -StartY * H ) # set scroll
        
        this.TextEndX = this.TextStartX+(this.widget_width/W)
        
        this.TextEndY = StartY+1+(this.widget_height/H) # improve speed by only drawing what's shown
        maxnodes = this.rows.__len__()
        if this.TextEndY>maxnodes: this.TextEndY=maxnodes
        EndY = this.TextEndY

        docol = this.offset_column
        dscol = docol+this.size_column
        dtcol = dscol+(W*3) # relates to the text position
        vlcol = this.widget_width-this.value_column
        vlpos = vlcol+W

        collapsed = this.collapsed
        skip = 0
        for _i in collapsed:
            if skip<_i<StartY: skip+=collapsed[_i]
        
        for y in range(StartY,EndY-1):
            i = y+skip; y+=1
            if i>=maxnodes: break
            datatype,assignment,label,parents,children,expanded,_ln=this.rows[i]()
            if datatype==None: continue
            level = parents.__len__()-1
            # noinspection PySimplifyBooleanCheck
            if expanded==False: skip+=children # this is already simplified (bool(None) is False)
            Y=y*H
            
            data_offset = ('0x%s0%iX'%('%',this.offlen))%datatype.__addr__
            dow = data_offset.__len__()*W
            dopos = docol-(dow+W)
            
            data_size = '%s'%datatype.__size__
            dsw = data_size.__len__()*W
            dspos = dscol-(dsw+W)
            
            dtname='<%s>'%datatype.__name__
            dtw=dtname.__len__()*W
            dtpos = dtcol+(level*W2)
            
            #dtcolor = QtGui.QColor(datatype.__color__)
            #dtcolor.setAlpha(64)
            
            
            grayrow = this.grayRow if not y%2 else this.white
            
            this._painter.fillRect(0,Y,dscol,H,grayrow)
            
            this._painter.setPen(this.textColor)
            
            this._painter.drawText(dopos,Y,dow,H,Qt.AlignTop,data_offset)
            this._painter.drawText(dspos,Y,dsw,H,Qt.AlignTop,data_size)
            
            this._painter.fillRect(dtcol,Y,(dtpos-dtcol)+dtw,H,grayrow)
            
            this._painter.setPen(this.treeLineColor)
            for x,pn in enumerate(parents):
                X = dtcol+(x*W2)
                if pn.dt == None: continue
                pdtcolor = QtGui.QColor(pn.dt.__color__)
                pdtcolor.setAlpha(64)
                #if X>end: break
                this._painter.fillRect( X,Y,(dtpos-X)+dtw,H, pdtcolor) # (parent) data type color associated with the level
                if pn.notend: X-=W; this._painter.drawLine(X,Y,X,Y+H) # tree line
            
            if parents:
                X = dtcol+(level*W2)-W
                HH=H*.5; _Y=Y+HH; HW=W*.5; _X=X+HW
                if not parents[-1].notend: this._painter.drawLine(X,Y,X,_Y) # last node vertical line
                this._painter.drawLine(X,_Y,_X,_Y) # node line
                if expanded!=None: this.drawToggle( X,_Y, X-HW,_Y-HW,_X,_Y+HW, W, expanded )
            
            if this.selections[0]==i:
                #this._painter.fillRect( dtpos,Y,dtw+aw+(bool(n.assignment+n.label)*W)+lbw,H, dSelClr )
                this._painter.fillRect(dscol,Y,vlcol-dscol,H,dSelClr)
            
            this._painter.setPen(this.textColor)
            this._painter.drawText(dtpos,Y,dtw,H,Qt.AlignTop,dtname)
            
            apos = dtpos+dtw+W
            aw = assignment.__len__()*W
            this._painter.drawText(apos,Y,aw,H,Qt.AlignTop,assignment)
            
            if label:
                lbpos = apos+aw
                lbw = label.__len__()*W
                this._painter.setPen(this.labelColor); this._painter.drawText(lbpos,Y,lbw,H,Qt.AlignTop,label)
            
            this._painter.fillRect(vlcol,Y,this.value_column,H,grayrow)
            
            this._painter.setPen(this.textColor)
            name = datatype.__name__
            value = '' if 'struct' in name or 'array' in name else str(datatype)
            if name == 'string': value = "'%s'"%value
            vlw = value.__len__()*W
            this._painter.drawText(vlpos,Y,vlw,H,Qt.AlignTop,value)
        
        # lines and headers
        Top = StartY*H; Bottom = EndY*H#; T1 = Top+H
        
        painter.fillRect(0, Top, this.widget_width, H, this.headerColor ) # BG
        
        this._painter.setPen(this.lineColor)
        this._painter.drawLine(docol,Top,docol,Bottom)
        this._painter.drawLine(dscol,Top,dscol,Bottom)
        this._painter.drawLine(vlcol,Top,vlcol,Bottom)
        #this._painter.drawLine(0,T1,this.widget_width,T1)
        
        this._painter.setPen(this.textColor)
        ot = 'offset'; otw = ot.__len__()*W
        this._painter.drawText((docol/2)-(otw/2),Top,otw,H,Qt.AlignTop,ot)
        st = 'size'; stw = st.__len__()*W
        this._painter.drawText(docol+(this.size_column/2)-(stw/2),Top,stw,H,Qt.AlignTop,st)
        Dt = 'data'; Dtw = Dt.__len__()*W
        this._painter.drawText(dscol+((this.widget_width-dscol-this.value_column)/2)-(Dtw/2),Top,Dtw,H,Qt.AlignTop,Dt)
        vt = 'value'; vtw = vt.__len__()*W
        this._painter.drawText(vlcol+(this.value_column/2)-(vtw/2),Top,vtw,H,Qt.AlignTop,vt)
        
        
        '''
            if n.expandable and not n.expanded: skip+=this.skip(n.children)
            if y>=this.TextStartY:
                Y = y*H
                dt=n.dt
                #if not dt: continue
                for c in this.columns:
                    start = c.pos
                    end = start+c.width

                    if c.name=='Offsets':
                        this._painter.fillRect( start,Y,end,H, this.grayRow if not y%2 else this.white)
                        offset = ('0x%s0%iX'%('%',this.offlen))%dt.__addr__
                        w = len(offset)*W; pos = end-(w+W)
                        this._painter.setPen( this.textColor ); this._painter.drawText( pos,Y,w,H, Qt.AlignTop, offset)

                    if c.name=='Assignments':
                        level = len(n.levels)
                        dtname = dt.__name__
                        dtpos = start+(level*2*W); dtw = len(dtname)*W
                        apos = dtpos+dtw+W; aw = len(n.assignment)*W
                        lbpos = apos+aw; lbw = len(n.label)*W
                        # draw data type bg rectangles and tree lines
                        x = 0; this._painter.setPen( this.treeLineColor )
                        for l,pdtbgcol in n.levels+[(False,n.dtbgcolor)]:
                            X = start+(x*2*W); x+=1
                            if X>end: break
                            this._painter.fillRect( X,Y,(dtpos-X)+dtw,H, pdtbgcol) # (parent) data type color associated with the level
                            if l: X+=W; this._painter.drawLine(X,Y,X,Y+H) # tree line
                        if this.selections[0]==i:
                            #this._painter.fillRect( dtpos,Y,dtw+aw+(bool(n.assignment+n.label)*W)+lbw,H, dSelClr )
                            this._painter.fillRect( start,Y,c.width,H, dSelClr )
                        X = start+((((level-1)*2)+1)*W)
                        if X<=end: # draw text
                            this._painter.setPen( n.dtfgcolor ); this._painter.drawText( dtpos,Y,dtw,H, Qt.AlignTop, dtname)
                            if n.assignment: this._painter.setPen( n.fgcolor ); this._painter.drawText( apos,Y,aw,H, Qt.AlignTop, n.assignment)
                            if n.label: this._painter.setPen( this.labelColor ); this._painter.drawText( lbpos,Y,lbw,H, Qt.AlignTop, n.label)
                            if n.levels:
                                this._painter.setPen( this.treeLineColor )
                                HH = H*.5; _Y = Y+HH; HW = W*.5; _X = X+HW
                                if not n.levels[-1][0]: this._painter.drawLine(X,Y,X,_Y) # last node vertical line
                                this._painter.drawLine(X,_Y,_X,_Y) # node line
                                if n.expandable: this.drawExNode( X,_Y, X-HW,_Y-HW,_X,_Y+HW, W, n.expanded ) # draw toggle

                    if c.name=='Values':
                        dtvalue = dt.__value__
                        this._painter.fillRect( start,Y,end,H, this.grayRow if not y%2 else this.white)
                        this._painter.setPen( this.textColor )
                        if dtvalue.__class__ in (str,unicode):
                            pos=start+W; vsize=len(dtvalue)*W
                            this._painter.drawText( pos,Y,W,H, Qt.AlignTop, "'"); pos+=W
                            this._painter.drawText( pos,Y,vsize,H, Qt.AlignTop, dtvalue); pos+=vsize
                            this._painter.drawText( pos,Y,W,H, Qt.AlignTop, "'") # because unicode tends to bork when this character is added through "'"+n.value+"'"
                        else:
                            val = dtvalue.__str__()
                            this._painter.drawText( start+W,Y,len(val)*W,H, Qt.AlignTop, val)
                            
        # draw headers ( overdraw any column data )
        Y = this.TextStartY*H # first line
        lastcol = len(this.columns)
        for curcol,col in enumerate(this.columns):
            start = col.pos
            
            if 0<curcol<lastcol: # draw separator
                this._painter.setPen( this.lineColor )
                this._painter.drawLine(start,Y,start,Y+this.widget_height)
            else: # draw header BG
                painter.fillRect(0, Y, this.widget_width, H, this.headerColor ) # BG

            # draw title
            tw = len(col.name)*W
            tpos = start+((col.width*.5)-(tw*.5)) # center text
            if tpos<start: tpos = start
            this._painter.setPen( this.textColor )
            this._painter.drawText( tpos,Y,tw,H, Qt.AlignTop, col.name)
        '''
        painter.end()
        this.updateScrollbars()
        return

    #input events:
        
    def mouseDoubleClickEvent(self, event) :
        if(event.button() == Qt.LeftButton) :
            x = event.x(); y = event.y()
            '''
            if (x >= self.hexPos and x < self.textPos):
                #self.highlighting = True

                #self.selection_start = self.pixelToByte(x, y)
                self.selection_end = self.selection_start
            '''
            self.repaint()

        return
 
 
    def mousePressEvent(this, event):
        if(event.button() == Qt.LeftButton):
            
            this.repaint()

        return
        
    def mouseMoveEvent(self, event) :
        return
 
    def mouseReleaseEvent(this, event) :
        W,H = this.font_width,this.font_height
        Y = (this.verticalScrollBar().value()-1)*H
        x,y = event.x(),event.y()+Y
        
        dscol = this.offset_column+this.size_column
        vlcol=this.widget_width-this.value_column
        if not dscol<x<vlcol: return
        
        collapsed = this.collapsed
        mi = y/H
        i = 0
        for _i in collapsed:
            if i<_i<mi: i+=collapsed[_i]
        
        this.selections = [None]
        #this.ondeselect()
        
        
        if i>len(this.rows)-1: return
        
        ss=dscol+(W*3) # relates to the text position
        n=this.rows[i]
        
        if n.expanded != None:
            W2 = W*2; HW=W*.75
            ex,ey=ss+(((len(n.parents)-1)*W2)-W),(mi*H)+(H/2)
            if ex-HW<x<ex+HW and ey-HW<y<ey+HW:
                if n.expanded: this.collapsed[i] = n.children
                else: this.collapsed.pop(i,None)
                n.expanded=not n.expanded
                this.repaint()
                return
        se = (vlcol-ss)/2
        if ss<x<se: this.selections=[i]; this.repaint(); this.onselect()
 
    def scrollTo( self, offset) :
        self.updateScrollbars()
        self.verticalScrollBar().setValue(offset)
        self.repaint()
        return

    def keyPressEvent(this, event) :
        key = event.key()
        mod = event.modifiers()
        if (mod & Qt.ControlModifier) :
            
            if key == Qt.Key_Home: this.scrollTo(0)
            if key == Qt.Key_End: this.scrollTo(this.numLines)
            '''
            elif key == Qt.Key_Down:
                while True:
                    offset = self.verticalScrollBar().value() * (self.row_width * self.group_width)
                    if(offset + 1 < self.data.size) :
                        self.scrollTo(offset + 1)
                    #return so we don't pass on the key event
                    return
                
            elif key == Qt.Key_Up:
                while True:
                    offset = self.verticalScrollBar().value() * (self.row_width * self.group_width)
                    if(offset > 0) :
                        self.scrollTo(offset - 1)
                    #return so we don't pass on the key event
                    return
            '''
        else:
            #print key
            if 31<key<128: # normal key press
                pass
            this.repaint()


        #QtGui.QAbstractScrollArea.keyPressEvent(this,event)
        return
