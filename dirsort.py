from datetime import datetime
import glob
import os
import pathlib
from time import sleep
from PIL import Image
from playsound import playsound
import pygame
import vlc
import random



def do_log(message):
	dateX = datetime.now().strftime("%Y-%m-%d")
	timeX = datetime.now().strftime(" %H:%M:%S")
	file1 = open(dateX + "-moved.log", "a")
	file1.write(dateX + timeX + " " + message + "\n")
	file1.close()

def debug_print(message):
	print("")
	print(message + " [DEBUGGING]")
	print("")
	sleep(0.1)


def preview_file(fname):

	debug_print("in preview_file")

	exten = pathlib.Path(fname).suffix.strip(".").upper()
	
	if exten == 'PNG' or exten == 'JPG' or exten == 'JPEG':
		print("Opening IMAGE to preview: ", fname)
		try:
			Image.open(fname).show()
		except Exception as e: 
			print('Exception opening file')
			print(e)
			
	elif exten == 'MP3':
			
		try:
		
			print("Opening AUDIO with pygame: ")
			print(" ", fname)
			
			pygame.mixer.init()  # initialize mixer module
			pygame.mixer.music.load(fname)
			pygame.mixer.music.play()

			confirmation("Press enter to stop")
			
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()
		
			return

		except Exception as e: 
			print('Exception opening file with pygame')
			print(e)
			
		try:
		
			print("Opening AUDIO with playsound: ")
			print(" ", fname)

			playsound(fname)
			
			return
		except Exception as e: 
			print('Exception opening file with playsound')
			print(e)
			
		try:
		
			print("Opening AUDIO with vlc: ")
			print(" ", fname)

			p = vlc.MediaPlayer(fname)
			p.play()
			p.stop()
			
			return
		except Exception as e: 
			print('Exception opening file with vlc')
			print(e)

			
	elif exten == 'TXT' or exten == 'SQL' or exten == 'PY' or exten == 'LOG':
	
		f = open(fname, "r")
		for x in f:
			print(x.rstrip())
			sleep(0.1)
	else:
		print(exten, ' extension cannot be previewed')



def getfolders(dircheck):

	golist = {"0": ".."}

	folders = 0

	for file in glob.glob(dircheck+"/*"):
		if os.path.isdir(file):
			folders = folders + 1
			golist[str(folders)] = pathlib.Path(file).stem

	return golist


def pickfolder(starting):

	debug_print("in pickfolder")

	dircheck = os.path.abspath(starting)
	
	while True:

		picked = None
		folders = 0
		lineitem("Currently in", dircheck)
		lineitem("  Browse " + str(folders), "..")

		topSummary = foldersummary(dircheck)

		for file in glob.glob(dircheck+"/*"):
			if os.path.isdir(file):
			
				thisSummary = foldersummary(file)				
				folders = folders + 1
				longerlineitem("  Browse " + str(folders), pathlib.Path(file).stem, "Folders: " + str(thisSummary["folders"]), "Files: " + str(thisSummary["files"]))
				
				if folders % 20 == 0 and folders < 100:
					sleep(3)

		
		if topSummary["files"] > 0:
			lineitem("", "---------------------------")
			lineitem("  list", "List " + str(topSummary["files"]) + " files!")
			lineitem("  sort", "Sort " + str(topSummary["files"]) + " files!")
			lineitem("  melt", "Melt this folder!")
			lineitem("", "---------------------------")

		if picked == None:
		
			tmp = folderquery("Which folder do you want to enter? ")
			
			if tmp == 'exit':
				return {"action" : "exit"}
			elif tmp == '..':
				picked = 0
			elif tmp == 'list':
				return {"action" : "list", "folder" : os.path.abspath(dircheck)}
			elif tmp == 'melt':
				return {"action" : "melt", "folder" : os.path.abspath(dircheck)}
			elif tmp == 'sort':
				return {"action" : "sort", "folder" : os.path.abspath(dircheck)}
			else:
				try:
					picked = int(tmp)
				except:
					continue

		folders = 0

		if picked == 0:
			dircheck = os.path.abspath(dircheck+"/..")
		else:
			for file in glob.glob(dircheck+"/*"):	
				if os.path.isdir(file):
					folders = folders + 1
					if folders == picked:
						dircheck = os.path.abspath(file)



def foldersummary(dircheck):

	files = 0
	folders = 0
	size = 0

	for file in glob.glob(dircheck+"/*"):
	
		if os.path.isfile(file):
			files = files + 1
			size = size + os.path.getsize(file)
		else:
			folders = folders + 1

	return {"path": dircheck, "files": files, "folders": folders, "size": size}


def sortfolder(response):

	debug_print("in sortfolder")
	
	dircheck = response["folder"]
	
	if response["action"] == 'sort':
		for file in glob.glob(dircheck+"/*"):
			if os.path.isfile(file):
			
				summary = foldersummary(dircheck)
				
				lineitem("Directory", os.path.abspath(dircheck))
				lineitem("  Files Left", str(summary["files"]))
				
				fresponse = sortfile(response, file)
				
				if fresponse["action"] == 'exit':
					break
					
	elif response["action"] == 'list':
	
		fileCount = 0
	
		for file in glob.glob(dircheck+"/*"):
			if os.path.isfile(file):
				fileCount = fileCount + 1
				lineitem("  File " + str(fileCount), pathlib.Path(file).name)
				
				if fileCount % 20 == 0 and fileCount < 100:
					sleep(3)
				
		confirmation("End of file list")
				
	elif response["action"] == 'melt':
	
		print(response)
	
		for file in glob.glob(dircheck+"/*"):
			movefile(file, pathlib.Path(file).parent.parent)

		confirmation("Folder will be deleted: " + dircheck)

		try:
			os.rmdir(dircheck)
		except Exception as e: 
			print(e)





def easyoptions(map, question):
	for key in map:
		lineitem(key, map[key])
	
	lineitem('other', 'enter a custom value not listed')
	inputx = input(question)
	
	if inputx == '':
		return inputx
	
	if inputx == 'other':
		return input('What custom value do you want? ')
	
	value = map.get(inputx)
	
	if value != '' and value != None:
		return value

	return easyoptions(map, question)



def detecttimeframe(timeframes, file):

	for key in timeframes:
		if timeframes[key] == pathlib.Path(file).parent.stem:
			return timeframes[key]
		elif timeframes[key] == pathlib.Path(file).parent.parent.stem:
			return timeframes[key]
		
	return None



def sortfile(response, file):

	dircheck = response["folder"]

	debug_print("in sortfile")
	debug_print("File location: " + file)
	
	lineitem("File", pathlib.Path(file).name)
	lineitem("Size", str(os.path.getsize(file)))
		
	rootmap = {"q":"is actionable this quarter"}
	rootmap["a"] = "is actionable this year"
	rootmap["s"] = "is someday"
	rootmap["r"] = "is reference"
	rootmap["c"] = "is completed"
	rootmap["t"] = "is trash"
	rootmap["n"] = "is not sure"
	rootmap["o"] = "open"
	rootmap["exit"] = "exit"


	timeframefound = detecttimeframe(rootmap, file)
	
	if timeframefound is not None:
		lineitem('Time frame', timeframefound)
		folder = timeframefound
	else:
		folder = easyoptions(rootmap, 'What timeframe? ')
	
	if folder == 'open':
		preview_file(file)
		
		appending = input('What should we append to the file name to describe it? ')
	
		if appending != '':
			dest = pathlib.Path(file)
			dest = str(dest.parent) + '/' + str(dest.stem) + '-' + appending + str(dest.suffix)
			os.rename(file, dest)
			lineitem('New Name', dest)
			sleep(3)
			return sortfile(response, dest)
		else:
			return sortfile(response, file)
			
	elif folder == 'exit':
		return {"action" : "exit"}
	elif folder != '':
		
		actmap = {"b":"books"}
		actmap["bs"] = "buy at store"
		actmap["bo"] = "buy online"
		actmap["ed"] = "education-classes"
		actmap["e"] = "events"
		actmap["me"] = "find an outlet for media"
		actmap["p"] = "places"
		actmap["r"] = "read"
		actmap["re"] = "recipe"
		actmap["c"] = "research at computer"
		actmap["w"] = "watch"
		actmap["wr"] = "write to list"		
		
		if folder == 'is actionable this quarter' or folder == 'is actionable this year' or folder == 'is someday':
			
			actmap.update(getfolders(dircheck + '/' + folder))
			subfolder = easyoptions(actmap, 'Choose a subfolder: ')
				
			if subfolder != '':
				folder = folder + '/' + subfolder

		elif folder == 'is reference':
		
			refmap = {"h":"health", "f":"finances", "r":"relationships", "s":"spiritual", "l":"living-space", "p": "photos"}

			refmap.update(getfolders(dircheck + '/' + folder))
			
			subfolder = easyoptions(refmap, 'Choose a subfolder: ')
				
			if subfolder != '':
				folder = folder + '/' + subfolder
			
		newpath = dircheck + '/' + folder
		
		if not os.path.exists(newpath):
			os.makedirs(newpath)
			
		movefile(file, newpath)
		return {"action": "moved", "folder": folder, "file": file}
	else:
		return {"action" : "", "folder" : folder}
		
		
def lineitem(key, value):

	if len(key) > 0:
		key = key + ":"
		
	print(key.ljust(15, " ") + value)
	sleep(0.05)


def longerlineitem(key, val1, val2, val3):
	lineitem(key, val1.ljust(30, " ") + val2.ljust(15, " ") + val3.ljust(10, " "))


def confirmation(message):
	input("*** " + message)
	


def folderquery(message):
	entered = input(message)
	
	if entered == 'melt':
		if input('Are you sure? (y/n) ') == 'y':
			return entered
	elif entered != '':
		return entered
		
	return folderquery(message)


def movefile(current, dest):
	dest = str(dest) + "/" + pathlib.Path(current).name
	
	try:
		if os.path.isdir(dest):
			dest = dest + '/' + pathlib.Path(current).name + '-conflict-' + str(random.randrange(1000,9999))

		lineitem('Current', current)
		lineitem('Destination', dest)
		
		os.rename(current, dest)
		
		do_log('BEFORE ' + current)
		do_log('AFTER  ' + dest)
		
	except Exception as e: 
		print(e)

	

dircheck = input("Which drive letter to start with? ").strip()

if dircheck == '' or dircheck == '.':
	dircheck = '.'
else:
	dircheck = dircheck + ':'

while True:

	debug_print("in main loop")
		
	response = pickfolder(dircheck)

	if response["action"] == 'exit':
		print('Exiting now')
		sleep(2)
		break
	else:
		dircheck = response["folder"]
		
	sortfolder(response)
