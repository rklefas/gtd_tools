import glob
import os
import pathlib
from time import sleep
from PIL import Image


def debug_print(message):
	print("")
	print(message + " [DEBUGGING]")
	print("")


def preview_file(fname):

	file_extension = pathlib.Path(fname).suffix.upper()
	
	if file_extension == '.PNG' or file_extension == '.JPG':
		print("Opening image to preview: ", fname)
		
		try:
			Image.open(fname).show()
		except:
			print('Exception opening file')



def pickfolder(starting):

	debug_print("in pickfolder")

	dircheck = os.path.abspath(starting)
	
	while True:

		picked = None
		folders = 0
		files = 0
		lineitem("Currently in", dircheck)
		lineitem("Browse " + str(folders), "..")

		for file in glob.glob(dircheck+"/*"):
		
			if os.path.isfile(file):
				files = files + 1

			if os.path.isdir(file):
				folders = folders + 1
				lineitem("Browse " + str(folders), file.replace(dircheck, ""))
		
		if files > 0:
			lineitem("", " ")
			lineitem(".", "Sort " + str(files) + " files!")
			lineitem("", " ")

		if picked == None:
		
			tmp = input("  Which folder do you want to enter? ")
			
			if tmp == '..':
				picked = 0
			elif tmp == '.':
				picked = 999
			else:
				try:
					picked = int(tmp)
				except:
					continue

		folders = 0

		if picked == 999:
			return os.path.abspath(dircheck)
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

	
	lineitem("  Files", str(files))
	
	if (files > 0):
		for file in glob.glob(dircheck+"/*"):	
			if os.path.isfile(file):
				if sortfile(dircheck, file) == 'exit':
					break



def sortfile(dircheck, file):

	debug_print("in sortfile")
	
	preview_file(file)
	
	lineitem("File", file.replace(dircheck, ""))
	lineitem("options", "exit, open")
	lineitem("", "(a)ctionable this year")
	lineitem("", "(s)omeday")
	lineitem("", "(r)eference")
	lineitem("", "(n)ot sure")

	folder = input("  >>> When actionable? [a s r n] ")
	
	
	if folder == 'exit':
		return folder
		
	if folder != '':
		
		if folder == 'a':
			folder = 'is actionable'
		elif folder == 's':
			folder = 'is someday'
		elif folder == 'r':
			folder = 'is reference'
		elif folder == 'n':
			folder = 'is not sure'
			
		newpath = dircheck + '/' + folder
		
		if not os.path.exists(newpath):
			os.makedirs(newpath)

		os.rename(file, file.replace(dircheck, newpath))

	return 'moved to ' + folder

def lineitem(key, value):

	if len(key) > 0:
		key = key + ":"
		
	print(key.ljust(15, " ") + value)
	sleep(0.05)


def confirmation(message):
	input("*** " + message)
	

dircheck = input("Which drive letter to start with? ").strip()

if dircheck == '' or dircheck == '.':
	dircheck = '.'
else:
	dircheck = dircheck + ':'

while True:

	debug_print("in main loop")
		
	dircheck = pickfolder(dircheck)

	if dircheck == 'exit':
		break
		
	sortfolder(dircheck)
