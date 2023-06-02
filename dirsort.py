from datetime import datetime
import glob
import os
import pathlib
from time import sleep
from playsound import playsound
import pygame
import random
import re
import json
from collections import Counter


def globber(ex):

	first = datetime.now().strftime("%H:%M:%S")
	xx = sorted(glob.glob(ex))
	second = datetime.now().strftime("%H:%M:%S")

	if first != second:
		print(first, second, ex)

	return xx


def clear_cache(filter = ""):
	for file in globber("./cache/*" + filter + "*.txt"):
		os.remove(file)


def slug_path(dir):
	dateX = os.path.abspath(dir)
	dateX = dateX.replace('\\', '-')
	dateX = dateX.replace('/', '-')
	dateX = dateX.replace('*', '-')
	dateX = dateX.replace(':', '-')
	return dateX


def dirfetch(type, dir):
	dateX = slug_path(dir)
	fp = open('cache/' + type + '-' + dateX + ".txt", "r")
	return json.load(fp)


def dirput(type, dir, data):
	dateX = slug_path(dir)	
	file = 'cache/' + type + '-' + dateX + ".txt"
	
	print('Created', file)
	
	fp = open(file, "w")
	json.dump(data, fp, indent=2)
	fp.close()

	return dirfetch(type, dir)
  


def do_log(message):
	dateX = datetime.now().strftime("%Y-%m-%d")
	timeX = datetime.now().strftime(" %H:%M:%S")
	file1 = open('logs/' + dateX + "-moved.log", "a")
	file1.write(dateX + timeX + " " + message + "\n")
	file1.close()

def debug_print(message):
	print("")
	print(message + " [DEBUGGING]")
	print("")
	sleep(0.01)


def preview_file(fname):

	# debug_print("in preview_file")

	exten = pathlib.Path(fname).suffix.strip(".").upper()
	
	if exten == 'URL' and ' archive]' not in fname:
		
		yearInput = input('Load which year? ')
		
		if len(yearInput) > 0:
			archiveName = fname.replace('.url', ' [' + yearInput + ' archive].url')
			archiveUrl = 'https://web.archive.org/web/' + yearInput + '/'
		
			with open(fname, 'r') as file:
				data = file.read()
				
			data = data.replace('URL=', 'URL=' + archiveUrl)

			text_file = open(archiveName, "w")
			text_file.write(data)
			text_file.close()

			os.startfile(archiveName)
			
		os.startfile(fname)

	elif exten == 'MP3':
			
		try:
		
			print("Opening AUDIO with pygame: ")
			print(" ", fname)
			
			pygame.mixer.init()	 # initialize mixer module
			pygame.mixer.music.load(fname)
			pygame.mixer.music.play()

			confirmation("Press enter to stop")
			
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()

		except Exception as e: 
			print('Exception opening file with pygame')
			print(e)
			
			try:
			
				print("Opening AUDIO with playsound: ")
				print(" ", fname)
				playsound(fname)
				
			except Exception as e: 
				print('Exception opening file with playsound')
				print(e)
			
	else:
		print(exten, ' extension loading using default program')
		os.startfile(fname)

		
		
	appending = input('What should we append to the file name to describe it? ')

	if len(appending) > 2:
		dest = append_rename(fname, appending)
		lineitem('New Name', dest)
		sleep(2)
		return str(dest)
	else:
		return str(fname)



def append_rename(fname, appending):
	dest = pathlib.Path(fname)
	dest = str(dest.parent) + '/' + str(dest.stem) + '-' + appending + str(dest.suffix)
	os.rename(fname, dest)
	
	return dest
	

def dedupemap(mapping):

	newmap = {}
	listx = []
	
	for key in mapping:	
		valux = mapping.get(key)

		if valux not in listx:
			listx.append(valux)	
			newmap[key] = valux

	return newmap


def getfolders(dircheck):

	try:
		gotback = dirfetch('getfolders', dircheck)
		return gotback
	except:
		golist = {"0": ".."}

		folders = 0

		for file in globber(dircheck+"/*"):
			if os.path.isdir(file):
				folders = folders + 1
				golist[str(folders)] = pathlib.Path(file).stem

		return dirput('getfolders', dircheck, golist)


def pickfolder(starting):

	# debug_print("in pickfolder")

	dircheck = os.path.abspath(starting)
	
	while True:

		picked = None
		folders = 0
		lineitem("Currently in", dircheck)

		topSummary = foldersummary(dircheck)
		gotten = getfolders(dircheck)

		# Preload cache data
		for file in gotten.values():
			thisSummary = foldersummary(dircheck + '/' + file)				


		for file in gotten.values():

			thisSummary = foldersummary(dircheck + '/' + file)				
			
			if thisSummary["folders"] > 0:
				folderItem = "Folders: " + str(thisSummary["folders"])
			else:
				folderItem = ""
			
			if thisSummary["files"] > 20:
				fileItem = "! Files: " + str(thisSummary["files"])
			elif thisSummary["files"] > 0:
				fileItem = "Files: " + str(thisSummary["files"])
			else:
				fileItem = ""

			if thisSummary["files"] > 0:
				sizeItem = "Size: " + human_readable_size(thisSummary["size"], 1)
			else:
				sizeItem = ""

			longerlineitem("  Browse " + str(folders), pathlib.Path(file).stem, folderItem, fileItem, sizeItem)
			
			if folders > 0 and folders % 20 == 0 and folders < 100:
				sleep(2)
				
			folders = folders + 1

		
		if topSummary["files"] > 0:
			lineitem("", "---------------------------")
			lineitem("	list", "List " + str(topSummary["files"]) + " files!")
			
			for xx in topSummary["extensions"]:
				lineitem("	  ." + str(xx),	 str(topSummary["extensions"].get(xx)))
				
			lineitem("	sort", "Sort " + str(topSummary["files"]) + " files!")
			lineitem("	melt", "Melt this folder!")
			lineitem("", "---------------------------")

		if picked == None:
		
			tmp = folderquery("Which folder do you want to enter? ")
			
			if tmp == 'exit':
				return {"action" : "exit"}
			elif tmp == '..':
				picked = 0
			elif tmp == 'list':

				filter = input("Filter by filename? ")
			
				return {"action" : "list", "filter": filter, "folder" : os.path.abspath(dircheck)}
			elif tmp == 'clear' or tmp == 'common' or tmp == 'melt':
				return {"action" : tmp, "folder" : os.path.abspath(dircheck)}
			elif tmp == 'sort':
			
				filter = input("Filter by filename? ")
			
				return {"action" : "sort", "filter": filter, "folder" : os.path.abspath(dircheck)}
			else:
				try:
					picked = int(tmp)
				except:
					continue

		folders = 0

		if picked == 0:
			dircheck = os.path.abspath(dircheck+"/..")
		else:
			gets = getfolders(dircheck).get(str(picked))
			dircheck = os.path.abspath(dircheck + '/' + gets)


def human_readable_size(size, decimal_places=2):
	for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
		if size < 1024.0 or unit == 'PiB':
			break
		size /= 1024.0
	
	if unit == 'B':
		decimal_places = 0
		
	return f"{size:.{decimal_places}f} {unit}"


def foldersummary(dircheck):

	try:
		gotback = dirfetch('foldersummary', dircheck)
		return gotback
	except:

		files = 0
		folders = 0
		size = 0
		extensions = {}

		for file in globber(dircheck+"/*"):
		
			if os.path.isfile(file):
			
				exten = pathlib.Path(file).suffix.strip(".")	
				value = extensions.get(exten)
		
				if value == None:
					extensions[exten] = 1
				else:
					extensions[exten] = value + 1
			
				files = files + 1
				size = size + os.path.getsize(file)
			else:
				folders = folders + 1

		golist = {"path": dircheck, "files": files, "folders": folders, "size": size, "extensions": extensions}
		
		return dirput('foldersummary', dircheck, golist)




def sortfolder(response):

	# debug_print("in sortfolder")
	
	dircheck = response["folder"]
	
					
	if response["action"] == 'list':
	
		fileCount = 0
	
		for file in globber(dircheck + "/*" + response["filter"] + '*'):
			if os.path.isfile(file):
				fileCount = fileCount + 1
				lineitem("	File " + str(fileCount), pathlib.Path(file).name)
				
				if fileCount % 20 == 0 and fileCount < 100:
					sleep(2)
				
		if input('Do you want to sort these files? (y/n) ') == 'y':
			response["action"] = 'sort'
			
			
			
	if response["action"] == 'sort':
		for file in globber(dircheck + "/*" + response["filter"] + '*'):
			if os.path.isfile(file):
				
				lineitem("Directory", os.path.abspath(dircheck))
				
				fresponse = sortfile(response, file)
				
				if fresponse["action"] == 'exit':
					break


	if response["action"] == 'common':
	
		text = ''
		
		for file in globber(dircheck+"/*"):
			text = text + ' ' + pathlib.Path(file).stem

		counts =  Counter(re.findall('\w+', text))
		shown = 0
		
		for wordum in counts.most_common():
			if len(wordum[0]) > 3 and wordum[1] > 1:
				shown = shown + 1
				lineitem(wordum[0], str(wordum[1]))
				
				if shown % 20 == 0:
					if confirmation('Common words shown ' + str(shown) + ' ') == 'exit':
						break


	if response["action"] == 'clear':
		clear_cache()

	if response["action"] == 'melt':
	
		print(response)
		
		append = input('What do you want to append to the file names? ')
	
		for file in globber(dircheck+"/*"):
		
			if len(append) > 0:
				file = append_rename(file, append)
		
			movefile(file, pathlib.Path(file).parent.parent)

		confirmation("Folder will be deleted: " + dircheck)

		try:
			os.rmdir(dircheck)
			clear_cache(pathlib.Path(file).parent.parent.stem)
		except Exception as e: 
			print(e)





def easyoptions(map, question):

	columns = 0
	outstring = ""

	for key in map:
		outstring = outstring + str('  ' + key + ' = ' + map[key]).ljust(30, " ")
		columns = columns + 1
		
		if columns == 3:
			print(outstring)
			outstring = ""
			columns = 0
	
	print(outstring)

	lineitem('other', 'enter a custom value not listed')
	print("")
	inputx = input(question)
	
	if inputx == '':
		return inputx
	
	if inputx == 'other':
		return input('What custom value do you want? ')
	
	value = map.get(inputx)
	
	if value != '' and value != None:
		return value

	return easyoptions(map, question)



def giveoptionset(sets):

	if sets == 'root':
	
		refmap = {"up": "..", "o": "open", "exit": "exit"}
		refmap["a"] = "is actionable"
		refmap["s"] = "is someday"
		refmap["r"] = "is reference"
		refmap["c"] = "is completed"
		refmap["t"] = "is trash"
		refmap["n"] = "is not sure"
		
	elif sets == 'is actionable' or sets == 'is someday':
	
		refmap = {"up": "..", "o": "open", "exit": "exit"}
		refmap["b"] = "books"
		refmap["bs"] = "buy at store"
		refmap["bo"] = "buy online"
		refmap["ed"] = "education-classes"
		refmap["e"] = "events"
		refmap["ex"] = "expert service"
		refmap["me"] = "find an outlet for media"
		refmap["p"] = "places"
		refmap["r"] = "read"
		refmap["re"] = "recipe"
		refmap["c"] = "research at computer"
		refmap["w"] = "watch"
		refmap["wr"] = "write to list"

	elif sets == 'priority':
	
		refmap = {"up": "..", "o": "open", "exit": "exit"}
		refmap["ps"] = "purchase, product, or service"
		refmap["lv"] = "long term value"
		refmap["h"] = "high interest"
		refmap["m"] = "medium interest"
		refmap["l"] = "low interest"
		refmap["n"] = "not sure"
		
	elif sets == 'is reference':
	
		refmap = {"up": "..", "o": "open", "exit": "exit"}
		refmap["f"] = "finances"
		refmap["l"] = "living-space"
		refmap["h"] = "health"
		refmap["p"] = "photos"
		refmap["r"] = "relationships"
		refmap["s"] = "spiritual"
		refmap["t"] = "travel"
		
	else:
		refmap = {"up": "..", "o": "open", "exit": "exit"}
		
	return refmap



def detectoptionset(timeframes, file):

	for key in timeframes:
		if 'is trash' == pathlib.Path(file).parent.stem:
			return 'done'
		elif 'is completed' == pathlib.Path(file).parent.stem:
			return 'done'
		elif 'is not sure' == pathlib.Path(file).parent.stem:
			return 'done'
		elif 'is reference' == pathlib.Path(file).parent.stem:
			return 'is reference'
		elif 'is reference' == pathlib.Path(file).parent.parent.stem:
			return 'basic'
		elif 'is reference' == pathlib.Path(file).parent.parent.parent.stem:
			return 'basic'
		elif timeframes[key] == pathlib.Path(file).parent.stem:
			return timeframes[key]
		elif timeframes[key] == pathlib.Path(file).parent.parent.stem:
			return "priority"
		elif timeframes[key] == pathlib.Path(file).parent.parent.parent.stem:
			return "done"
		elif timeframes[key] == pathlib.Path(file).parent.parent.parent.parent.stem:
			return "done"
		
	return "root"



def nameisgarbage(file):
	
	txt = pathlib.Path(file).stem
	txt = txt.replace("Screenshot_", "")
	txt = txt.replace("IMG_", "")
	txt = txt.replace("_Chrome", "")
	txt = txt.replace("_YouTube", "")
	txt = txt.replace("_Textra", "")
	txt = txt.replace("-", "")
	txt = txt.replace("_", "")
	txt = txt.replace("1", "")
	txt = txt.replace("2", "")
	txt = txt.replace("3", "")
	txt = txt.replace("4", "")
	txt = txt.replace("5", "")
	txt = txt.replace("6", "")
	txt = txt.replace("7", "")
	txt = txt.replace("8", "")
	txt = txt.replace("9", "")
	txt = txt.replace("0", "")
	
	if len(txt) == 0:
		return True
	else:
		return False


def sortfile(response, file):

	# debug_print("in sortfile")
	
	rootmap = giveoptionset('root')
	detected = detectoptionset(rootmap, file)
	
	if detected == 'done':
		return {"action": "", "folder": response["folder"], "file": file}
	
	lineitem("File", pathlib.Path(file).name)
		
	newpath = response["folder"]
	newfilelocation = file

	refmap = giveoptionset(detected)
	refmap.update(getfolders(newpath))
	refmap = dedupemap(refmap)

	if nameisgarbage(newfilelocation):
		newfilelocation = preview_file(newfilelocation)

	subfolder = easyoptions(refmap, detected + ' option set, pick one: ')

	if subfolder != '':
	
		if subfolder == 'open':
			newfilelocation = preview_file(newfilelocation)
			return sortfile(response, newfilelocation)
		elif subfolder == 'exit':
			return {"action" : "exit"}

		newpath = newpath + '/' + subfolder
		
		if not os.path.exists(newpath):
			os.makedirs(newpath)
			clear_cache('getfolders')

			
		newfilelocation = movefile(newfilelocation, newpath)
		
		return sortfile({"action": "moved", "folder": newpath}, newfilelocation)
		
	return {"action": "moved", "folder": newpath, "file": newfilelocation}

		
		
def lineitem(key, value):

	if len(key) > 0:
		key = key + ":"
		
	print(key.ljust(15, " ") + value)
	sleep(0.01)


def longerlineitem(key, val1, val2, val3, val4):
	lineitem(key, val1.ljust(30, " ") + val2.ljust(15, " ") + val3.ljust(15, " ") + val4)


def confirmation(message):
	return input("*** " + message)
	


def folderquery(message):
	entered = input(message)
	
	if entered == 'melt':
		if input('Are you sure? (y/n) ') == 'y':
			return entered
	elif entered != '':
		return entered
		
	return folderquery(message)


def movefile(current, dest):

	if pathlib.Path(current).name == 'Thumbs.db':
		os.remove(current)
		do_log('DELETE ' + current)
		return ''

	dest = str(dest) + "/" + pathlib.Path(current).name
	
	try:
		if os.path.isdir(dest):
			dest = dest + '/' + pathlib.Path(current).name + '-conflict-' + str(random.randrange(1000,9999))

		if os.path.isfile(dest):
			dest = dest + '-' + str(random.randrange(1000,9999)) + '.duplicate'

		lineitem('Current', current)
		lineitem('Destination', dest)
		
		os.rename(current, dest)
		
		do_log('MOVE ' + current)
		do_log('  TO ' + dest)
		
		return dest
		
	except Exception as e: 
		print(e)

	

dircheck = input("Which drive letter to start with? ").strip()

if dircheck == '' or dircheck == '.':
	dircheck = '.'
else:
	dircheck = dircheck + ':'

while True:

	# debug_print("in main loop")
		
	try:
		response = pickfolder(dircheck)

		if response["action"] == 'exit':
			clear_cache()
			print('Exiting now')
			sleep(2)
			break
		else:
			dircheck = response["folder"]
			
		sortfolder(response)
		
	except Exception as e:
		print(e)
		confirmation('The system has recoved from a major failure')

