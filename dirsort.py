from datetime import datetime
import glob
import os
import pathlib
from time import sleep
from PIL import Image
from playsound import playsound
import pygame
import vlc



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
	
	if exten == 'PNG' or exten == 'JPG':
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

			
	elif exten == 'TXT' or exten == 'SQL' or exten == 'PY':
	
		f = open(fname, "r")
		for x in f:
			print(x.rstrip())
			sleep(0.1)
	else:
		print(exten, ' extension cannot be previewed')



def pickfolder(starting):

	debug_print("in pickfolder")

	dircheck = os.path.abspath(starting)
	
	while True:

		picked = None
		folders = 0
		files = 0
		lineitem("Currently in", dircheck)
		lineitem("  Browse " + str(folders), "..")

		for file in glob.glob(dircheck+"/*"):
		
			if os.path.isfile(file):
				files = files + 1

			if os.path.isdir(file):
				folders = folders + 1
				lineitem("  Browse " + str(folders), pathlib.Path(file).stem)
				
				if folders % 20 == 0:
					sleep(3)

		
		if files > 0:
			lineitem("", "---------------------------")
			lineitem("  list", "List " + str(files) + " files!")
			lineitem("  sort", "Sort " + str(files) + " files!")
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
	summary = foldersummary(dircheck)
	files = summary["files"]

	lineitem("Directory", os.path.abspath(dircheck))
	
	if response["action"] == 'sort':
		for file in glob.glob(dircheck+"/*"):
			if os.path.isfile(file):
			
				lineitem("Directory", os.path.abspath(dircheck))
				lineitem("  Files", str(files))
				
				fresponse = sortfile(response, file)
				
				if fresponse["action"] == 'exit':
					break
					
	elif response["action"] == 'list':
	
		fileCount = 0
	
		for file in glob.glob(dircheck+"/*"):
			if os.path.isfile(file):
				fileCount = fileCount + 1
				lineitem("  File " + str(fileCount), pathlib.Path(file).name)
				
				if fileCount % 20 == 0:
					sleep(3)
				
		confirmation("End of file list")
				
	elif response["action"] == 'melt':
	
		print(response)
	
		for file in glob.glob(dircheck+"/*"):
			movefile(file, pathlib.Path(file).parent.parent)

		confirmation("Folder will be deleted: " + dircheck)

		os.rmdir(dircheck)


def printmap(map):
	for key in map:
		lineitem(key, map[key])
		
	return input('>>> Put in subfolder? ')


def foldermap(map, index):

	value = map.get(index)
	
	if value != '' and value != None:
		return value
		
	return index


def sortfile(response, file):

	dircheck = response["folder"]

	debug_print("in sortfile")
	
	lineitem("File", pathlib.Path(file).name)
	lineitem("Size", str(os.path.getsize(file)))
	
	lineitem("options", "exit, (o)pen, append")
	lineitem("", "(q)ctionable this quarter")
	lineitem("", "(a)ctionable this year")
	lineitem("", "(s)omeday")
	lineitem("", "(r)eference")
	lineitem("", "(c)ompleted")
	lineitem("", "(t)rash")
	lineitem("", "(n)ot sure")

	folder = input(">>> When actionable? [q/a/s/r/c/t/n] ")
	
	if folder == 'open' or folder == 'o':
		preview_file(file)
		return sortfile(response, file)
	elif folder == 'append':
	
		appending = input('What should we append to the file name? ')
	
		dest = pathlib.Path(file)
		dest = str(dest.parent) + '/' + str(dest.stem) + '-' + appending + str(dest.suffix)
		
		os.rename(file, dest)
		lineitem('New Name', dest)
		sleep(5)
		
		return sortfile(response, dest)
	elif folder == 'exit':
		return {"action" : "exit"}
	elif folder != '':
		
		actmap = {"b":"books", "bs": "buy at store", "bo": "buy online", "ed": "education", "e":"events", "p":"places", "r": "read", "w": "watch", "c": "research at computer"}
		
		if folder == 'q':
			folder = 'is actionable this quarter'
			
			subfolder = printmap(actmap)
				
			if subfolder != '':
				folder = folder + '/' + foldermap(actmap, subfolder)

		elif folder == 'a':
			folder = 'is actionable'
			
			subfolder = printmap(actmap)
				
			if subfolder != '':
				folder = folder + '/' + foldermap(actmap, subfolder)

		elif folder == 's':
			folder = 'is someday'
		elif folder == 'r':
		
			folder = 'is reference'
			
			map = {"h":"health", "f":"finances", "r":"relationships", "s":"spiritual", "l":"living-space"}
			
			subfolder = printmap(map)
			
			if subfolder != '':
				folder = folder + '/' + foldermap(map, subfolder)

		elif folder == 'n':
			folder = 'is not sure'
		elif folder == 'c':
			folder = 'is completed'
		elif folder == 't':
			folder = 'is trash'
			
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
	os.rename(current, dest)
	
	do_log('BEFORE ' + current)
	do_log('AFTER  ' + dest)
	
	lineitem('Current', current)
	lineitem('Destination', dest)
	

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
