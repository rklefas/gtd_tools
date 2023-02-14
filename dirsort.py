import glob

while True:

	dircheck = input("What directory should we look at? ")
	
	if dircheck == 'exit':
		break
	
	for file in glob.glob(dircheck+"/*"):
		print(file)
		
		
		