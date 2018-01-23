# -*- coding: utf-8 -*-
import sys # NOTE: we cannot import anything other than sys

if sys.platform == 'win32':
    for i,p in enumerate(sys.path):
        if "C:\\Python27" in p: sys.path.pop(i) # remove C:\Python27 directories
    #add base directories
    sys.path.append(sys.executable.replace('python.exe','DLLs') )
    sys.path.append(sys.executable.split('win')[0]+'PyLib')
else:
    pass
    # noinspection PyCompatibility
    print sys.executable # print_function can't be imported here, __future__ is defined in PyLib/
    
CWD = __file__.split('SIDE')[0]
sys.path.append(CWD[:-1])

import os
# TODO: remove:
sys.path.append(os.path.sep.join((CWD+'app', 'PyLib', 'site-packages')))

if sys.platform == 'win32':
    for i,p in enumerate(sys.path):
        if "C:\\Python27" in p: sys.path.pop(i) # remove some C:\Python27 directories again
'''
# set custom directory for loaded binaries
DLL_directory = os.path.sep.join( ( os.getcwd(), 'app', 'bin', sys.argv[1] ) )
os.environ['PATH'] = os.pathsep.join((os.environ['PATH'],DLL_directory))
'''
#-------------------------------------------------------------------------------
__future__ = __import__('__future__')
print_function = __future__.print_function

from .common import *
from . import common
from .Wrappers import mainWrapper

class window(QtGui.QMainWindow):
    Reload=False

    def __init__(this, parent=None):
        QtGui.QMainWindow.__init__(this,parent)

        ### Menu+Toolbars ######################################################

        # --- icons ---
        iconSize = QtCore.QSize(16,16)
        newIcon = QtGui.QIcon('SIDE/images/default/new.png')
        openIcon = QtGui.QIcon('SIDE/images/default/open.png')
        saveIcon = QtGui.QIcon('SIDE/images/default/fileSave.png')
        saveAsIcon = QtGui.QIcon('SIDE/images/default/fileSaveAs.png')
        scriptIcon = QtGui.QIcon('SIDE/images/default/filePython.png')
        cutIcon = QtGui.QIcon('SIDE/images/default/editCut.png')
        copyIcon = QtGui.QIcon('SIDE/images/default/editCopy.png')
        pasteIcon = QtGui.QIcon('SIDE/images/default/editPaste.png')
        deleteIcon = QtGui.QIcon('SIDE/images/default/editDelete.png')
        undoIcon = QtGui.QIcon('SIDE/images/default/editUndo.png')
        redoIcon = QtGui.QIcon('SIDE/images/default/editRedo.png')
        runIcon = QtGui.QIcon('SIDE/images/default/1rightarrow.png')
        helpIcon = QtGui.QIcon('SIDE/images/default/help.png')
        aboutIcon = QtGui.QIcon('SIDE/images/default/helpAbout.png')
        
        # --- init/structuring ---
        fileMenu = QtGui.QMenu("File", this); this.menuBar().addMenu(fileMenu)
        templateMenu = QtGui.QMenu("New", this); templateMenu.setIcon(newIcon)
        for scope in scripts.scopes:
            scopeType=scope[4:-7].capitalize()
            tA = QtGui.QAction(scriptIcon,'',this, visible=False, triggered=this.action_newScript)
            tA.setText('%s Script'%scopeType); tA.setData([scope,scopeType]); tA.setVisible(True)
            templateMenu.addAction(tA)
        openMenu = QtGui.QMenu("Open", this); openMenu.setIcon(openIcon)
        for s in [_script for _script in os.listdir('scripts') if _script.endswith('py')]: # > *script*
            sA = QtGui.QAction(scriptIcon,'',this, visible=False, triggered=this.action_openScript)
            sA.setText(s); sA.setData('scripts/%s'%s); sA.setVisible(True)
            openMenu.addAction(sA)
        editMenu = QtGui.QMenu("Edit", this); this.menuBar().addMenu(editMenu)
        debugMenu = QtGui.QMenu("Debug", this); this.menuBar().addMenu(debugMenu)
        helpMenu = QtGui.QMenu("Help", this); this.menuBar().addMenu(helpMenu)
        
        fileToolBar = this.addToolBar("File"); fileToolBar.setIconSize(iconSize)
        debugToolBar = this.addToolBar("Debug"); debugToolBar.setIconSize(iconSize)
        helpToolBar = this.addToolBar("Help"); helpToolBar.setIconSize(iconSize)

        # --- actions ---
        # [File]
        this.newAct = QtGui.QAction(newIcon, "New", this); this.newAct.setMenu(templateMenu)
        this.newAct2 = QtGui.QAction(newIcon, "", this); this.newAct2.setMenu(templateMenu)
        this.openAct = QtGui.QAction(openIcon, "Open", this, shortcut=QtGui.QKeySequence.Open, triggered=this.action_openScript); this.openAct.setMenu(openMenu)
        this.openAct2 = QtGui.QAction(openIcon, "", this, triggered=this.action_openScript); this.openAct2.setMenu(openMenu)
        this.saveAct = QtGui.QAction(saveIcon, "Save", this, shortcut=QtGui.QKeySequence.Save, triggered=this.action_save)
        this.saveAct.setEnabled(False)
        this.saveAct2 = QtGui.QAction(saveIcon, "", this, triggered=this.action_save); this.saveAct2.setEnabled(False)
        this.saveAsAct = QtGui.QAction(saveAsIcon, "Save As", this, triggered=this.action_saveAs)
        this.saveAsAct2 = QtGui.QAction(saveAsIcon, "", this, triggered=this.action_saveAs)
        # [Edit]
        this.cutAct = QtGui.QAction(cutIcon, "Cut", this, shortcut=QtGui.QKeySequence.Cut, triggered=this.action_cut)
        this.cutAct2 = QtGui.QAction(cutIcon, "", this, triggered=this.action_cut)
        this.copyAct = QtGui.QAction(copyIcon, "Copy", this, shortcut=QtGui.QKeySequence.Copy, triggered=this.action_copy)
        this.copyAct2 = QtGui.QAction(copyIcon, "", this, triggered=this.action_copy)
        this.pasteAct = QtGui.QAction(pasteIcon, "Paste", this, shortcut=QtGui.QKeySequence.Paste, triggered=this.action_paste)
        this.pasteAct2 = QtGui.QAction(pasteIcon, "", this, triggered=this.action_paste)
        this.deleteAct = QtGui.QAction(deleteIcon, "Delete", this)#, triggered=)
        this.deleteAct2 = QtGui.QAction(deleteIcon, "", this)#, triggered=)
        this.undoAct = QtGui.QAction(undoIcon, "Undo", this)#, triggered=)
        this.undoAct2 = QtGui.QAction(undoIcon, "", this)#, triggered=)
        this.redoAct = QtGui.QAction(redoIcon, "Redo", this)#, triggered=)
        this.redoAct2 = QtGui.QAction(redoIcon, "", this)#, triggered=)
        # [Debug]
        this.openTFAct = QtGui.QAction(openIcon, "Open Test File", this, triggered=this.action_openTestFile); this.openTFAct.setEnabled(False)
        this.openTFAct2 = QtGui.QAction(openIcon, "", this, triggered=this.action_openTestFile); this.openTFAct2.setEnabled(False)
        this.runAct = QtGui.QAction(runIcon, "Run", this, shortcut=QtGui.QKeySequence(Qt.Key_F5), triggered=this.action_go); this.runAct.setEnabled(False)
        this.runAct2 = QtGui.QAction(runIcon, "", this, triggered=this.action_go); this.runAct2.setEnabled(False)
        # [Help]
        this.helpAct = QtGui.QAction(helpIcon, "View Help", this)#, triggered=)
        this.helpAct2 = QtGui.QAction(helpIcon, "", this)#, triggered=)
        this.aboutAct = QtGui.QAction(aboutIcon, "About SIDE", this, triggered=this.action_about)
        this.aboutAct2 = QtGui.QAction(aboutIcon, "", this, triggered=this.action_about)
        
        # --- display ---
        # [File]
        fileMenu.addAction(this.newAct)
        fileMenu.addAction(this.openAct)
        fileMenu.addAction(this.saveAct)
        fileMenu.addAction(this.saveAsAct)
        fileMenu.addSeparator() # -----
        fileMenu.addAction('Exit', this.closeEvent) # Exit
        fileMenu.addAction('Reload', this.action_reload) # Reload
        fileToolBar.addAction(this.newAct2)
        fileToolBar.addAction(this.openAct2)
        fileToolBar.addAction(this.saveAct2)
        fileToolBar.addAction(this.saveAsAct2)
        fileToolBar.addSeparator()
        # [Edit]
        editMenu.addAction(this.undoAct)
        editMenu.addAction(this.redoAct)
        editMenu.addSeparator()
        editMenu.addAction(this.cutAct)
        editMenu.addAction(this.copyAct)
        editMenu.addAction(this.pasteAct)
        editMenu.addAction(this.deleteAct)
        fileToolBar.addAction(this.cutAct2)
        fileToolBar.addAction(this.copyAct2)
        fileToolBar.addAction(this.pasteAct2)
        fileToolBar.addAction(this.deleteAct2)
        fileToolBar.addSeparator()
        fileToolBar.addAction(this.undoAct2)
        fileToolBar.addAction(this.redoAct2)
        # [Debug]
        debugMenu.addAction(this.runAct); debugToolBar.addAction(this.runAct2)
        debugMenu.addAction(this.openTFAct); debugToolBar.addAction(this.openTFAct2)
        # [Help]
        helpMenu.addAction(this.helpAct); helpToolBar.addAction(this.helpAct2)
        helpMenu.addAction(this.aboutAct); helpToolBar.addAction(this.aboutAct2)
        ### /Menu+Toolbars #####################################################
        
        this.documents = QtGui.QTabWidget()
        this.documents.setTabsClosable(True)
        #this.documents.setMovable(True)
        # this is stupid: (why no callback instead)
        QtCore.QObject.connect( this.documents, QtCore.SIGNAL("currentChanged(int)"), this.tabChange )
        QtCore.QObject.connect( this.documents, QtCore.SIGNAL("tabCloseRequested(int)"), this.tabClose )
                
        this.setCentralWidget(this.documents)
        this.status = this.statusBar()
        
        this.status.showMessage("Ready")
        #this.update_selectors()

        this.setWindowTitle("UGE Script IDE")
        this.openScripts = {}

    def tabChange(this,tabIndex):
        if len(this.openScripts)>0:
            T = len(this.documents.widget(tabIndex).openFiles)!=0
        else:
            T = False
            this.openTFAct.setEnabled( False )
            this.openTFAct2.setEnabled( False )
        this.runAct.setEnabled( T )
        this.runAct2.setEnabled( T )

    # noinspection PyShadowingNames
    def tabClose(this,tabIndex):
        MW = this.documents.widget(tabIndex)
        if MW.editor.unsaved:
            ret = QtGui.QMessageBox.warning(this, "Application",
                "The document has been modified.\nDo you want to save your changes?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save: this.action_save(); this.tabClose(tabIndex)
            elif ret == QtGui.QMessageBox.Cancel: return
            elif ret == QtGui.QMessageBox.Discard: MW.editor.unsaved=False; this.tabClose(tabIndex)
        else:
            while len(MW.openFiles)>0: MW.tabClose(0)
            for f,i in this.openScripts.items():
                if i==tabIndex: this.openScripts.pop(f)
                if i>tabIndex: this.openScripts[f]-=1
            this.documents.removeTab(tabIndex)
            del MW

    # noinspection PyUnusedLocal,PyShadowingNames
    def closeEvent(this, event=None): # overloaded
        #TODO: selectable group-save dialog
        save = False
        if any([this.documents.widget(i).editor.unsaved for i in range(len(this.openScripts))]):
            ret = QtGui.QMessageBox.warning(this, "Application", "Would you like to save your changes?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save: save = True
            elif ret == QtGui.QMessageBox.Cancel: return

        while len(this.openScripts)>0:
            if save: this.documents.setCurrentWidget(0); this.action_save()
            else: this.documents.widget(0).editor.unsaved = False
            this.tabClose(0)
        QtGui.qApp.quit(); sys.exit(0)
    
    def action_newScript(this):
        scope,Type = map(str,this.sender().data().toPyObject())
        text = ("ugeScriptType( %s )\n"
                "%s"
                "#ugeScriptLibs([ 'library' ])\n"
                "\n%s"
                "def ugeImport%s( FileType, UI ):\n"
                "    ##your code here\n"
                "    return\n"
                "\n"
                "def ugeExport%s( FileType, UI ):\n"
                "    ##your code here\n"
                "    return\n"
                )%( scope,
                    ( "ugeScriptFormats({ 'Compression Standard Description': ['standard'] }) # eg: 'Zlib': ['zlib']\n"
                        if Type=='Compression' else "ugeScriptFormats({ '%s Format Description': ['fmt'] })\n"%Type ),
                    '' if Type=='Compression' else (
                        "def uge%sImportUI( UI ): pass\n"
                        "\n"
                        "def uge%sExportUI( UI ): pass\n"
                        "\n"
                        )%( Type, Type ),
                    Type, Type )
        
        scriptName = 'New_%s_Script.py'%Type; ID=2
        while scriptName in this.openScripts: scriptName = 'New_%s_Script_%i.py'%(Type,ID); ID+=1
        
        wrapper = mainWrapper(this)
        this.openScripts[scriptName] = this.documents.addTab(wrapper, '%s *'%scriptName)
        wrapper.editor.setText(text)
        wrapper.editor.file = scriptName
        wrapper.editor.unsaved = True
            
        this.documents.setCurrentIndex(this.openScripts[scriptName])
        this.setWindowTitle("UGE Script IDE - %s"%scriptName)
        
        this.openTFAct.setEnabled(True)
        this.openTFAct2.setEnabled(True)
        
        this.status.showMessage("Ready")
        
    def action_openScript(this):
        action = this.sender()
        path = action.data().toString()
        
        #this.status.showMessage("")
        
        if path == '': path = QtGui.QFileDialog.getOpenFileName(this, "Open File", '', "UGE Python scripts (*.py)")
        
        if path!='':
            scriptName = path.split('/')[-1]
            
            if scriptName not in this.openScripts:
                with open(path,'rb') as inFile: text = inFile.read()
                wrapper = mainWrapper(this)
                this.openScripts[scriptName] = this.documents.addTab(wrapper, scriptName)
                wrapper.editor.setText(text)
                wrapper.editor.file = path

            this.documents.setCurrentIndex(this.openScripts[scriptName])
            this.setWindowTitle("UGE Script IDE - %s"%scriptName)
            
            this.openTFAct.setEnabled(True)
            this.openTFAct2.setEnabled(True)

        this.status.showMessage("Ready")
    
    @staticmethod
    def action_reload( ):
        # noinspection PyBroadException
        try:
            f = open(sys.argv[0],'rb')
            src = f.read(); f.close()
            exec src in {}
            
            python = sys.executable
            os.execl(python, python, * sys.argv)
        except: 
            typ, val, tb = sys.exc_info() #;tb=traceback.extract_tb(i[2])[0]
            print()
            traceback.print_exception(
                typ,val,tb#,
                #limit=2,
                #file=sys.stdout
                )
            print()
            
    def action_about(this): pass
    
    def action_openTestFile(this): this.documents.currentWidget().openTestFile(); this.status.showMessage("Ready")
    def action_go(this):
        this.action_save()
        this.documents.currentWidget().go()
        this.status.showMessage("Ready")

    # noinspection PyShadowingNames
    def action_save(this): 
        editor = this.documents.currentWidget().editor
        if editor.file=='': this.action_saveAs()
        else:
            with open(editor.file,'wb') as outFile: outFile.write(editor.code)
            editor.unsaved = False
            this.saveAct.setEnabled(False)
            this.saveAct2.setEnabled(False)
            i = this.documents.currentIndex()
            this.documents.setTabText(i,editor.file.split('/')[-1])
    def action_saveAs(this):
        path = QtGui.QFileDialog.getSaveFileName(this)
        if path:
            this.documents.currentWidget().editor.file = path
            this.action_save()
            
    def action_cut(this): this.documents.currentWidget().editor.action_cut()
    def action_copy(this): this.documents.currentWidget().editor.action_copy()
    def action_paste(this): this.documents.currentWidget().editor.action_paste()

def run():
    import sys
    
    app = QtGui.QApplication(sys.argv)
    '''
    app.setStyleSheet("""
        QToolTip {
            border: 2px solid silver;
            border-radius: 7px;
            padding: 0px 1px 0px 1px;
            background-color: white;
            color: SteelBlue;
            font-size: 9pt;
            font-family: Courier New;
            }""")
    '''
    # sys.modules['/SIDE_cursor/'] = QtGui.QCursor()
    sys.modules['/SIDE_clipboard/'] = app.clipboard()

    # TODO: loadModifiers()
    common.loadLibraries()
    common.scripts.load()

    # only way I could get this working with less confusion:
    # (setting a global var in common didn't work)
    sys.modules['/SIDE_window/'] = window()
    sys.modules['/SIDE_window/'].resize(640, 512)
    sys.modules['/SIDE_window/'].show()
    sys.exit(app.exec_())

if __name__ == '__main__': run()
