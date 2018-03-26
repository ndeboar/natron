#Deadline submitter for Natron, borrowed heavily from:
#https://github.com/CGRU/cgru/blob/master/plugins/natron/afanasy.py
#And Deadline's Nuke submission scripts

import os
import sys
import subprocess
from os.path import expanduser


# Natron:
import NatronEngine
import NatronGui

def EncodeAsUTF16String( unicodeString ):
    return unicodeString.decode( "utf-8" ).encode( "utf-16-le" )

def getProjectPaths( i_app):

	data = i_app.getProjectParam('projectPaths').getValue()

	words = []
	for path in data.split('</Name>'):
		words.extend( path.split('</Value>'))

	names = []
	for word in words:
		word = word.replace('<Name>','')
		word = word.replace('<Value>','')
		word = word.strip()
		if len(word): names.append(word)

	paths = dict()
	i = 0
	while i < len(names):
		paths[names[i]] = names[i+1]
		i += 2

	return paths



def GetDeadlineCommand():
    deadlineBin = ""
    try:
        deadlineBin = os.environ['DEADLINE_PATH']
    except KeyError:
        #if the error is a key error it means that DEADLINE_PATH is not set. however Deadline command may be in the PATH or on OSX it could be in the file /Users/Shared/Thinkbox/DEADLINE_PATH
        pass
        
    # On OSX, we look for the DEADLINE_PATH file if the environment variable does not exist.
    if deadlineBin == "" and  os.path.exists( "/Users/Shared/Thinkbox/DEADLINE_PATH" ):
        with open( "/Users/Shared/Thinkbox/DEADLINE_PATH" ) as f:
            deadlineBin = f.read().strip()

    deadlineCommand = os.path.join(deadlineBin, "deadlinecommand")
    
    return deadlineCommand

def CallDeadlineCommand( arguments ):
    deadlineCommand = GetDeadlineCommand()
    
    startupinfo = None
    #~ if os.name == 'nt':
        #~ startupinfo = subprocess.STARTUPINFO()
        #~ startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    arguments.insert( 0, deadlineCommand)
    
    # Specifying PIPE for all handles to workaround a Python bug on Windows. The unused handles are then closed immediatley afterwards.
    proc = subprocess.Popen(arguments, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    proc.stdin.close()
    proc.stderr.close()
    
    output = proc.stdout.read()
    
    return output

def renderSelected():
	home = expanduser("~")
	deadlineTemp = os.path.join( home, "temp" )
	deadlineTemp = home

	app = NatronGui.natron.getActiveInstance()
	app = NatronGui.natron.getGuiInstance(app.getAppID())
	nodes = app.getSelectedNodes()

	path =  getProjectPaths(app)['Project']
	proj = app.getProjectParam('projectName').getValue()
	projPath =  ('%s/%s'%(path,proj))

	index = 0
	for node in nodes:
		nameName = node.getLabel()
		print ("Submitting %s" %nameName)
		fFrame = node.getParam('firstFrame').get()
		lFrame = node.getParam('lastFrame').get()
		writePath = node.getParam('filename').get()
		jobInfoFile = os.path.join( deadlineTemp, u"natron_submit_info.job")
		fileHandle = open( jobInfoFile, "w" )
		fileHandle.write( "Plugin=Natron\n" )
		fileHandle.write( "Name=%s - %s\n"%(proj, nameName))
		fileHandle.write( "ConcurrentTasks=3\n")
		fileHandle.write( "Frames=%d-%d\n" %(fFrame,lFrame) )
		fileHandle.write( "ChunkSize=5\n" )
		fileHandle.write( EncodeAsUTF16String( "OutputFilename%s=%s\n" % (index, writePath ) ) )
		fileHandle.write( EncodeAsUTF16String( "OutputDirectory%s=%s\n" % ( index, path ) ) )
		fileHandle.close()

		pluginInfoFile = os.path.join( deadlineTemp, u"natron_plugin_info.job")
		fileHandle = open( pluginInfoFile, "w" )
		fileHandle.write( "WriterNodeName=%s\n" % nameName )
		fileHandle.write( "ProjectFile=%s\n" %projPath )
		fileHandle.write( "Build=64bit")

		fileHandle.close()
		index +=1

		print CallDeadlineCommand([jobInfoFile, pluginInfoFile])


'''
fileHandle.write( "ConcurrentTasks=%s\n" % dialog.concurrentTasks.value() )

tempFrameList = str(int(comp.startFrame())) + "-" + str(int(comp.endFrame()))

fileHandle.write( "Frames=%s\n" % tempFrameList )
fileHandle.write( "ChunkSize=1\n" )

fileHandle.write( EncodeAsUTF16String( "OutputFilename%s=%s\n" % (index, paddedPath ) ) )
fileHandle.write( EncodeAsUTF16String( "OutputDirectory%s=%s\n" % ( index, tempPath ) ) )
i think index can just be any int that for each write node

'''