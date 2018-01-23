# -*- coding: utf-8 -*-
from SIDE.common import *

#from SIDE.treeViewer import treeView
from SIDE.HexViewer import HexView as hexView
from SIDE.TextViewer import TextView as textView

# holds the tree, file data, and gl viewers

class subWrapper(QtGui.QSplitter):
    def __init__(this, parent):
        QtGui.QSplitter.__init__(this, parent)
        this.setOrientation(QtCore.Qt.Horizontal)
        this.setHandleWidth(3)

        this.fdata = ''
        this.GoData = []
        
        # Go Button:
        GoButton = QtGui.QPushButton("Go ->\n(F5)")
        GoButton.setMinimumWidth(50)
        GoButton.setMaximumWidth(50)
        #GoButton.setMaximumHeight(25)
        #GoButton.AddAction(self.Go)
        QtCore.QObject.connect(GoButton, QtCore.SIGNAL("clicked()"), this.Go )
        
        #data tree viewer
        #this.treeView = treeView(this)
        #this.treeView.setColumnCount(2)
        #this.treeView.setHeaderLabels(['Function Call','Return Value'])
        
        viewSplit = QtGui.QSplitter()
        viewSplit.setOrientation(QtCore.Qt.Vertical)

        this.dataView = QtGui.QTabWidget()
        this.dataView.setMovable(False) #Not ready yet...
        this.dataView.setTabShape(this.dataView.Triangular)
        this.dataView.setTabPosition(this.dataView.South)
        this.dataView.addTab(hexView(this),'Hex')
        this.dataView.addTab(textView(this),'Text')
        #textView.setLineWrapMode(textView.NoWrap)

        this.glView = QtGui.QTabWidget()
        this.glView.setTabShape(this.glView.Triangular)
        this.glView.addTab(QtOpenGL.QGLWidget(),'Model')

        viewSplit.addWidget(this.dataView)
        viewSplit.addWidget(this.glView)
        
        #this.addWidget(this.treeView)
        this.addWidget(GoButton)
        this.addWidget(viewSplit)

    def Go(this): # run the import and export functions in the script
        lines = this.parent.editor.data.splitlines(1)
        this.GoData = [{}]*len(lines) # reset
        '''
        for token in tokenize.generate_tokens( iter(lines).next ):
            toktype, toktext, (srow, scol), (erow, ecol), line = token
            if toktype == tokenize.NAME: # we're only looking for function names
                raw = toktext # preserve the text to highlight

                try: # Test for a UMC (or UGE) data type from the given name
                    if toktext in ['u','s','f','h','bu','bs','bf','bh',]:
                        toktext = line[scol:]; toktext = toktext[:toktext.index(')')].replace('(','_') # 'bu'( 4 ) -> 'bu_4'
                        raw = line[scol:]; raw = raw[:raw.index(')')+1] #highlight 'bu( 4 )', not 'bu'
                    elif toktext in ['struct',]:
                        this.parent.editor.data
                        index = len(''.join(lines[:srow]))+ecol
                        r = 0
                        while True: # find the ')' in struct( )
                            try: c = this.parent.editor.data[index]
                            except: break
                            if c=='(': r+=1#; s+='\\'
                            if c==')': r-=1#; s+='\\'
                            raw+=c
                            if r==0: break
                            index+=1
                    else:
                        toktext = sys.modules['UGE_Type_Names'][toktext] # 'bu32' -> bu(4)
                        # ^ used for compairing types in UGE's data interface
                        if toktext.count('('): toktext = toktext.replace('(','_')[:-1] # 'bu(#)' -> 'bu_#'
                        # ^ the decorator, when calling bu32(), will come up with '__init__' for func.__name__
                        # when this occurs, the decorator will update to args[0].__class__.__name__ ('bu_4' for 'bu32')
                except KeyError: pass
                # ^ not a UGE data type
                # might be a UGE formatting or file system function (no modifications needed here)

                # now that we have the proper name referenced by the decorator,
                # we can include the column and original text associated with this name.
                try: sys.modules['UMC_SIDE_GO_CODE'][srow][toktext][0].append([raw,scol])
                except KeyError: sys.modules['UMC_SIDE_GO_CODE'][srow][toktext] = [[[raw,scol]],0]
                except IndexError: pass

        sys.modules['UMC_SIDE_TREE_CODE'] = []
        sys.modules['UGE_EXTERNAL'] = 'UMC_SIDE' # turn the decorator on (for this external program)

        # make sure the backend is on the same level we're on:
        TabIndex = self.tabBar.currentIndex()
        TestTabIndex = self.TestTabs[TabIndex].currentIndex()
        current_splitter = self.TestSplitters[TabIndex][TestTabIndex]
        current_hex_viewer = current_splitter.widget(2).widget(0).widget(0)
        # current_splitter.previewers.filedata_viewers.hex_viewer
        backend.FILE._current = current_hex_viewer.data
        current_hex_viewer.data.offset = 0
        current_hex_viewer.data_highlights = [(QtGui.QColor(255,255,255,255),0)]*current_hex_viewer.data.size
        
        #current_tree = current_splitter.widget(1)
        #current_tree.clear()
        '''

        try: # execute the given code in a pre-defined namespace:

            # build the namespace for the code (like UGE does)
            def Header(T,F,L,I): pass
            NS = {'Header':Header, 'UGE_MODEL':0}
            NS.update(backend.models) # TODO: supply functions based on any script type
            #NS.update(backend.__dict__)

            exec this.parent.editor.data+'\nugeImportModel(".typ",[])' in NS, {}
            # TODO: call ImportModel() from here

        except: # log the traceback, but continue running the program

            type, val, tb = sys.exc_info()#;tb = traceback.extract_tb(i[2])[0]
            print
            traceback.print_exception(
	            type, val, tb#,
	            #limit = 2
	            #file = sys.stdout
	            )
        
        #sys.modules['UGE_EXTERNAL'] = 'UGE' # turn the decorator off
        # ^ we don't want to test the function calls for every key-press in the editor
        # (reason for this is when you type an undefined data type such as bu(5)
        # which can only be registered by executing the code)
        #parent = [QtGui.QTreeWidgetItem(current_tree)]
        #parent[0].setExpanded(True)
        
        '''
        layer = 0 # TODO: check indentation when tokenizing

        for call in sys.modules['UMC_SIDE_TREE_CODE']:
            try: # test for data highlight
                codetext, coderow, codecol, datavalue, dataoffset, datasize, color = call
                for i in range(datasize):
                    current_hex_viewer.data_highlights[dataoffset+i] = (color,int(i==0))

                #item = QtGui.QTreeWidgetItem(parent[layer], [codetext,datavalue.__str__()])
                #item.setExpanded(True)

            except:
                codetext, coderow, codecol = call
                # append tree node

                #item = QtGui.QTreeWidgetItem(parent[layer], [codetext])
                #item.setExpanded(True)
                
        #current_tree.resizeColumnToContents(1)#'''
        
        #current_hex_viewer.repaint()
