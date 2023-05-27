import glob
import pathlib

#fp = open("keywords.json", "r")
#keywords = json.load(fp)

keywords = {}
folder = input('What folder? ')


for file in glob.glob(folder + '/*'):
	refile = pathlib.Path(file).stem
	matches = 0
	
	print(refile)
	
	
	for index in keywords:
		print(index)
		print(keywords.get(index))

		newfile = refile.replace(index, '[' + index + ']')
		if refile != newfile:
			refile = newfile
			matches = matches + 1
			print(newfile)
	
	if matches > 0:
		print('one or more matches found')
	else:
		key = input('No matches.  Enter a keyword to expand the library: ')

		if len(key) > 0:
			keywords[key] = 1