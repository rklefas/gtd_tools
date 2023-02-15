import glob
import os

def debug_print(message):
	print(message + " [DEBUGGING]")

def pickfolder(starting):

	debug_print("in pickfolder")

	dircheck = starting
	
	while True:

		picked = None
		folders = 0
		lineitem("Folder " + str(folders), "..")

		for file in glob.glob(dircheck+"/*"):
				
			if os.path.isdir(file):
				folders = folders + 1
				lineitem("Folder " + str(folders), file.replace(dircheck, ""))
				
		lineitem("Currently in", os.path.abspath(dircheck))

		if picked == None:
			picked = int(input("  Which folder do you want to enter? "))

		folders = 0

		if picked == 99:
			dircheck = os.path.abspath(dircheck)
			confirmation('You have chosen to sort: ' + dircheck)
			return dircheck
		elif picked == 0:
			dircheck = os.path.abspath(dircheck+"/..")
		else:
			for file in glob.glob(dircheck+"/*"):	
				if os.path.isdir(file):
					folders = folders + 1
					if folders == picked:
						dircheck = os.path.abspath(file)

		
def sortfolder(dircheck):

	debug_print("in sortfolder")

	lineitem("Directory", os.path.abspath(dircheck))
	
	files = 0
	folders = 0

	for file in glob.glob(dircheck+"/*"):
	
		if os.path.isfile(file):
			files = files + 1
#			lineitem("File", file.replace(dircheck, ""))
		else:
			folders = folders + 1
#			lineitem("Folder", file)

	
	print("There are "+ str(files) + " files in " + dircheck)
	
	if (files > 0):
		for file in glob.glob(dircheck+"/*"):	
			if os.path.isfile(file):
				sortfile(dircheck, file)



def sortfile(dircheck, file):

	debug_print("in sortfile")
	
	lineitem("File", file.replace(dircheck, ""))
	input("  Where should this go? ")

		
def lineitem(key, value):
	key = key + ":"
	print(key.ljust(15, " ") + value)


def confirmation(message):
	input("*** " + message)
	

while True:

	debug_print("in main loop")
	print("")
	print("")
	dircheck = input("What directory should we start with? ")
	
	if dircheck == 'exit':
		break
	
	dircheck = pickfolder(dircheck)
	sortfolder(dircheck)
