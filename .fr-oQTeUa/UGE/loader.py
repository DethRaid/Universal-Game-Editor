# -*- coding: utf-8 -*-
#NOTE: we cannot import anything other than sys
import sys

if sys.platform == 'win32':
    for i,p in enumerate(sys.path):
        if "C:\\Python27" in p: sys.path.pop(i) # remove C:\Python27 directories
    #add base directories
    sys.path.append(sys.executable.replace('python.exe','DLLs') )
    sys.path.append(sys.executable.split('win')[0]+'PyLib')
else:
    pass
    print(sys.executable)
    
CWD = __file__.split('loader')[0]
import os
#TODO: remove:
sys.path.append(os.path.sep.join((CWD+'app', 'PyLib', 'site-packages')))

if sys.platform == 'win32':
    for i,p in enumerate(sys.path):
        if "C:\\Python27" in p: sys.path.pop(i) # remove some C:\Python27 directories again


# set custom directory for loaded binaries
#DLL_directory = os.path.sep.join( ( os.getcwd(), 'app', 'bin', sys.argv[1] ) )
#os.environ['PATH'] = os.pathsep.join((os.environ['PATH'],DLL_directory))

'''
print
print sys.path
print 
'''#'''
#----------------------------------------------------------------------------------------------
# begin loader.py
from urllib import urlopen as Open

argLen = len(sys.argv)
if argLen > 1 and sys.argv[1] in ('x86','x64'):
    print("running in mode: '%s'" % sys.argv[1])
else: print("unknown mode, assuming x86")

print("\nChecking for updates...")

print("Failed: The server is currently unavailable.\n")

'''
def wait(T):
    while T > 0.0:
        if T > 1: time.sleep(1); sys.stdout.write('.')
        else: time.sleep(T)
        T -= 1
    print

try:
    Open("http://tcll5850.hostoi.com/Universal Model Converter/Connect.txt")
    CurVsn = U(">H", open("Version.dat", "rb").read(2))[0]
    SvrVsn = 1
    while True:
        try: Open("http://tcll5850.hostoi.com/Universal Model Converter/UMC/"+ str(SvrVsn) + ".py"); SvrVsn += 1
        except: IOError: break
    if SvrVsn > CurVsn:
        print "Update found!"
        I = raw_input("Would you like to install the update? (Y/N)").upper();print
        if I == "Y":
            keep_tryng = 1
            while keep_tryng:
                try:
                    print "Installing update"
                    UD = Open("http://tcll5850.hostoi.com/Universal Model Converter/UMC/" + str(SvrVsn)+".py")
                    Fl = open("API.py", "w")
                    Fl.write(UD.read())
                    open("Version.dat", "wb").write(U(">H", SvrVsn)[0])
                    print "Update complete!\n"
                    
                except IOError:
                    T = raw_input("Error: Connection lost... Try again? (Y/N)").upper()
                    if T == "Y": print "Retrying."; wait(2)
                    if T == "N": print "Update cancelled."; keep_tryng=0
    else: print "No update found.\n"

except: print "Could not establish a connection with the server.\n"
'''

if argLen > 2:
    print("loading file: %s" % sys.argv[2])
    if len(sys.argv) > 3:
        print("unable to import files:")
        for f in sys.argv[3:]: print("- %s" % f)
        print("please wait until v3.0, sorry :(")

# noinspection PyBroadException
try:
    import API
    API.run()
except:
    import traceback; print(); traceback.print_exception( *sys.exc_info() ); print()
    input("Press Enter to Exit.")


def BrawlNubsAttempt():
    print("Debugging. not finished yet. ")
