import glob
import os
import pathlib
from PIL import Image


def debug_print(message):
	print("")
	print(message + " [DEBUGGING]")
	print("")


def pickfolder(starting):

	debug_print("in pickfolder")

	dircheck = starting
	
	while True:

		picked = None
		folders = 0
		files = 0
		lineitem("Folder " + str(folders), "..")

		for file in glob.glob(dircheck+"/*"):
		
			if os.path.isfile(file):
				files = files + 1

			if os.path.isdir(file):
				folders = folders + 1
				lineitem("Folder " + str(folders), file.replace(dircheck, ""))
		
		lineitem("Currently in", os.path.abspath(dircheck))
		
		if files > 0:
			lineitem("Folder 99", "Sort current folder with " + str(files) + " files")

		if picked == None:
		
			tmp = input("  Which folder do you want to enter? ")
			
			if tmp == '..':
				picked = 0
			else:
				picked = int(tmp)

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
				if sortfile(dircheck, file) == 'exit':
					break



def sortfile(dircheck, file):

	debug_print("in sortfile")
	
	file_extension = pathlib.Path(file).suffix.upper()
	
	if file_extension == '.PNG' or file_extension == '.JPG':
		print("Opening image to preview: ", file)
		
		try:
			Image.open(file).show()
		except:
			print('Exception opening file')
			
	
	print("  (a)ctionable this year")
	print("  (s)omeday")
	print("  (r)eference")
	print("  (n)ot sure")

	folder = input(file.replace(dircheck, "")+" >>> When actionable? [a s r n]")
	
	if folder == 'exit':
		return folder
		
	if folder != '':
		
		if folder == 'a':
			folder = 'actionable'
		elif folder == 's':
			folder = 'someday'
		elif folder == 'r':
			folder = 'reference'
		elif folder == 'n':
			folder = 'not sure'
			
		newpath = dircheck + '/is ' + folder
		
		if not os.path.exists(newpath):
			os.makedirs(newpath)

		os.rename(file, file.replace(dircheck, newpath))

	return 'moved to ' + folder

def lineitem(key, value):
	key = key + ":"
	print(key.ljust(15, " ") + value)


def confirmation(message):
	input("*** " + message)
	

dircheck = "."

while True:

	debug_print("in main loop")
		
	dircheck = pickfolder(dircheck)

	if dircheck == 'exit':
		break
		
	sortfolder(dircheck)
