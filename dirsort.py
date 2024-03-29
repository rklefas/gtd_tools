from datetime import datetime
from datetime import timedelta
import glob
import os
import pathlib
from time import sleep
import pygame
import random
import re
import json
from collections import Counter
import shutil
import time

from win32com.client import Dispatch
from inputimeout import inputimeout, TimeoutOccurred


# ---------------
# ---------------

def prettyinput(q, defaultValue = None):
    print('')
    tmp = '<< ' + q + ' >> '
    
    if defaultValue != None:
        print(' *** Default value is', defaultValue)
    
    print('-' * len(tmp))
    xx = input(tmp)
    print('-' * len(tmp))
    
    if xx == '' and defaultValue != None:
        return defaultValue
    
    return xx

# ---------------
# ---------------

def print_divider():
    print('----------------------------------')
    
# ---------------


def inputcontrols(num = None):

    if num == None:
        num = prettyinput('What timeout for the inputs?  0 will turn off timeouts, empty will change nothing: ')
    

    if num == '0':
        dynamic_timeout = None
    elif num == '':
        print('No change to timeout setting')
    else:
        dynamic_timeout = int(num)
        
    return dynamic_timeout


def spokeninputtimeout(q, default, specific_timeout = None, tries = 1):
    
    for thistry in reversed(range(0, tries)):
    
        newtx = specific_timeout

        if newtx != None and newtx > 30:
            Dispatch("SAPI.SpVoice").Speak(q)
        
        try:
            print('')
            print_divider()
            print('  Enter == to alter timeout')
            print('  (' + str(newtx) + ' sec timeout, tries remain ' +str(thistry)+ ', default : ' + default + ')')

            val = inputimeout(q, newtx)

            print_divider()
            
            if val == '==':
                newtx = inputcontrols()
            
                if newtx == None:
                    return prettyinput(q, default)
                else:
                    return spokeninputtimeout(q, default, newtx, tries)
                
            return val
        except TimeoutOccurred:
            print_divider()

    if newtx != None and newtx > 30:
        Dispatch("SAPI.SpVoice").Speak('Defaulted to '+default)

    return default

# ---------------



def globber(ex, method = 'name asc'):

    first = datetime.now().strftime("%H:%M:%S")

    xx = glob.glob(ex)

    if method == 'ask' and len(xx) > 3:
        options = {}
        options['da'] = 'date asc'
        options['sa'] = 'size asc'
        options['na'] = 'name asc'
        options['dd'] = 'date desc'
        options['sd'] = 'size desc'
        options['nd'] = 'name desc'
        options['r'] = 'random'
    
        option = easyoptions(options, 'How do you want to sort the (' + str(len(xx)) + ') results? ')
    else:
        option = method
        
    if option == 'random':
        xx = sorted(xx, key=pushdate_random)
    elif option == 'size asc':
        xx = sorted(xx, key=pushdate_size)
    elif option == 'date asc':
        xx = sorted(xx, key=os.path.getmtime)
    elif option == 'name asc':
        xx = sorted(xx, key=pushdate_name)
    elif option == 'size desc':
        xx = sorted(xx, key=pushdate_size)
        xx.reverse()
    elif option == 'date desc':
        xx = sorted(xx, key=os.path.getmtime)
        xx.reverse()
    elif option == 'name desc':
        xx = sorted(xx, key=pushdate_name)
        xx.reverse()
        
    second = datetime.now().strftime("%H:%M:%S")

#   if first != second:
#       print(first, second, ex)

    return xx

# ---------------

def pushdate_name(filename):
    sortvalue = str(pathlib.Path(filename).stem).lower()
    delayed = parse_delaytime(filename)
    return delayed + ' ' + str(sortvalue)

# ---------------

def pushdate_random(filename):
    sortvalue = random.randrange(1000, 9999)
    delayed = parse_delaytime(filename)
    return delayed + ' ' + str(sortvalue)

# ---------------

def pushdate_size(filename):
    sortvalue = os.path.getsize(filename)
    delayed = parse_delaytime(filename)
    return delayed + ' ' + str(sortvalue).rjust(20, '0')


def parse_delaytime(filename):
    stem = str(pathlib.Path(filename).stem)
    if stem[0:3] == '{20':
        return stem[0:12]
    else:
        return datetime.now().strftime("{%Y-%m-%d}")



def print_block(xx, block = 25):
    down = int(len(xx) / block)

    return xx.ljust((down+1)*block, " ")


def show_file_and_metadata(heading, item):

    format = '%a %Y %b %d'

    if os.path.isfile(item):
        modification_time = time.localtime(os.path.getmtime(item))
        local_time = time.strftime(format, modification_time)
        
        lineitem(heading, local_time + '  ' + human_readable_size(os.path.getsize(item), 0).rjust(8, " ") + '   ' + pathlib.Path(item).name)
    elif os.path.isdir(item):
        modification_time = time.localtime(os.path.getmtime(item))
        local_time = time.strftime(format, modification_time)

        lineitem(heading, local_time + '   <DIR>     ' + os.path.abspath(item))
    else:
        lineitem('<MISSING>', item)


def render_int_for_grid(intval):
    return str(intval).rjust(4, " ")

def clear_cache(filter = ""):
    pattern = "./cache/*" + filter + ".json"
    files = globber(pattern)

    if len(files) > 0:
        if affirmative_answer('Clear ' + str(len(files)) + ' files from cache?  Pattern used: ' + pattern):
            for file in files:
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
    fp = open('cache/' + type + '-' + dateX + ".json", "r")
    return json.load(fp)


def dirput(type, dir, data):
    dateX = slug_path(dir)  
    file = 'cache/' + type + '-' + dateX + ".json"
        
    fp = open(file, "w")
    json.dump(data, fp, indent=2)
    fp.close()

    show_file_and_metadata('Cache File', file)

    return dirfetch(type, dir)
  


def do_log(message):
    dateX = datetime.now().strftime("%Y-%m-%d")
    timeX = datetime.now().strftime(" %H:%M:%S")
    file1 = open('logs/' + dateX + "-actions.log", "a")
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
        
        yearInput = input('Load which year? Leave empty to skip. ')
        
        if len(yearInput) > 0:
            archiveName = fname.replace('.url', ' [' + yearInput + ' archive].url')
            archiveUrl = 'https://web.archive.org/web/' + yearInput + '/'
        
            with open(fname, 'r') as file:
                data = file.read()
                
            data = data.replace('URL=', 'URL=' + archiveUrl)

            text_file = open(archiveName, "w")
            text_file.write(data)
            text_file.close()

            if affirmative_answer('We created an archive URL file.  Do you want to keep it? '):
                openfile(archiveName)
                os.remove(archiveName)
            else:
                openfile(archiveName)           
            
        openfile(fname)

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

        except Exception as e: 
            print('Exception opening file with pygame')
            print(e)
                        
    else:
        print(exten, ' extension loading using default program')
        openfile(fname)

        
        
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
    
    do_log(' REN ' + fname)
    do_log('  TO ' + dest)
    
    return dest
    

def push_rename(fname, prepending):

    pushing = prepending.replace('push to ', '')
    
    if pushing == '[date]':
        pushing = easyoptions(giveoptionset('(1 tomorrow)'), 'Push to? ')
        pushing = pushing.replace('push to ', '')

    finalpath = str(pathlib.Path(fname).parent)
    finalpath = finalpath.replace('\\', '/')
    finalpath = finalpath.replace('/(1 tomorrow)',      '')
    finalpath = finalpath.replace('/(2 this week)',     '')
    finalpath = finalpath.replace('/(3 this month)',    '')
    finalpath = finalpath.replace('/(4 this quarter)',  '')
    finalpath = finalpath.replace('/(5 this year)',     '')
    finalpath = finalpath.replace('/(6 this decade)',   '')
    finalpath = finalpath.replace('/(9 never)',         '')
    finalpath = finalpath.replace('/to watch',          '/to watch/[delay]')
    finalpath = finalpath.replace('/at computer',       '/at computer/[delay]')
    finalpath = finalpath.replace('/at home office',    '/at home office/[delay]')
    finalpath = finalpath.replace('/at outside',        '/at outside/[delay]')
    finalpath = finalpath.replace('/other context',     '/other context/[delay]')
    finalpath = finalpath.replace('/[delay]/[delay]',   '/[delay]')
    finalpath = finalpath.replace('/[delay]',           '/' + pushing)
   
    makenewdir(finalpath)
    result = movefile(fname, finalpath)
    
    return result



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
    back = foldersummary(dircheck)
    return back.get('dirs')



def pickfolder(starting, maxshow):

    # debug_print("in pickfolder")

    dircheck = os.path.abspath(starting)
    
    while True:

        picked = None
        folders = 0
        clearing()
        linedivider()
        show_file_and_metadata("Currently in", dircheck)
        linedivider()

        topSummary = foldersummary(dircheck)
        gotten = getfolders(dircheck).values()

        # Preload cache data
        for file in gotten:
            thisSummary = foldersummary(dircheck + '/' + file)              

        longerlineitem("", "-- FOLDER NAME ----------", "* FOLDERS *", "* FILES *", "* SIZE *")

        for file in gotten:

            thisSummary = foldersummary(dircheck + '/' + file)              
            
            if thisSummary["folders"] > 0:
                folderItem = render_int_for_grid(thisSummary["folders"])
            else:
                folderItem = ""
            
            if thisSummary["files"] > 0:
                fileItem = render_int_for_grid(thisSummary["files"])
            else:
                fileItem = ""

            if thisSummary["files"] > 0:
                sizeItem = human_readable_size(thisSummary["size"], 1)
            else:
                sizeItem = ""

            longerlineitem("<DIR> " + str(folders).rjust(2, " "), pathlib.Path(file).stem, folderItem, fileItem, sizeItem)
            
            if folders > 0 and folders % maxshow == 0:
                if affirmative_answer('Stop listing folders...') == True:
                    break
                else:
                    longerlineitem("", "-- FOLDER NAME ----------", "* FOLDERS *", "* FILES *", "* SIZE *")

                
                
            folders = folders + 1

        
        if topSummary["files"] > 0:
            linedivider()           
            comboline = ""

            for xx in topSummary["extensions"]:
                comboline = comboline + xx + ":" + str(topSummary["extensions"].get(xx)) + " "  

            lineitem(str(topSummary["files"]) + " files", comboline)
            
            if topSummary["delayed"] > 0:
                lineitem("Delayed files", str(topSummary["delayed"]))

        if picked == None:
        
            linedivider()
            tmp = folderquery("Select an option (help to show all) or pick a folder: ")
            
            if tmp == 'exit':
                return {"action" : "exit"}
            elif tmp == 'help':
            
                lineitem("sort", 'sort the files within this folder')
                lineitem("sort-dirs", 'sort the folders within this folder')
                lineitem("melt", 'melt this folder')
                lineitem("common", 'show most common keywords in filenames')
                lineitem("clear", 'clear performance cache')
                lineitem("list", 'list files in this folder')
                lineitem("explorer", 'open this folder in explorer')
                lineitem("quick-sort", '?')
                lineitem("exit", 'exit this program')
                
                confirmation('Press any key to exit help...')
                continue

            elif tmp == '..':
                picked = 0
            elif tmp == 'list':
                filter = ''
                return {"action" : "list", "filter": filter, "folder" : os.path.abspath(dircheck)}
            elif tmp == 'clear' or tmp == 'common' or tmp == 'melt' or tmp == 'explorer':
                return {"action" : tmp, "folder" : os.path.abspath(dircheck)}
            elif tmp == 'quick-sort':
                return {"action" : "quick-sort", "filter": '', "folder" : os.path.abspath(dircheck)}
            elif tmp == 'sort' or tmp == 'watch-sort':
                filter = input("Filter by filename? ")
                return {"action" : tmp, "filter": filter, "folder" : os.path.abspath(dircheck)}
            elif tmp == 'sort-dirs':
                filter = input("Filter by folder name? ")           
                return {"action" : "sort-dirs", "filter": filter, "folder" : os.path.abspath(dircheck)}
            else:
                try:
                    picked = int(tmp)
                except:
                    if os.path.isdir(dircheck + '/' + tmp):
                        dircheck = os.path.abspath(dircheck + '/' + tmp)
                    else:
                        confirmation(tmp + ' does not exist')

                    continue

        folders = 0

        if picked == 0:
            dircheck = os.path.abspath(dircheck+"/..")
        else:
            gets = getfolders(dircheck).get(str(picked))
            dircheck = os.path.abspath(dircheck + '/' + gets)


def human_readable_size(size, decimal_places=2):
    for unit in ['B  ', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    
    if unit == 'B  ':
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
        delayed = 0

        dirs = {"0": ".."}

        for file in globber(dircheck+"/*"):
        
            if os.path.isfile(file):
            
                exten = pathlib.Path(file).suffix.strip(".").lower()
                filename = pathlib.Path(file).stem
                value = extensions.get(exten)
        
                if value == None:
                    extensions[exten] = 1
                else:
                    extensions[exten] = value + 1
            
                files = files + 1
                size = size + os.path.getsize(file)
                
                if filename[0:3] == '{20':
                    delayed = delayed + 1
                
            elif os.path.isdir(file):
                folders = folders + 1
                dirs[str(folders)] = pathlib.Path(file).stem

        golist = {}
        golist["dirs"] = dirs
        golist["path"] = dircheck
        golist["files"] = files
        golist["folders"] = folders
        golist["size"] = size
        golist["extensions"] = extensions
        golist["delayed"] = delayed
        
        if files > 100:
            return dirput('foldersummary', dircheck, golist)
        else:
            return golist




def sortfolder(response):

    # debug_print("in sortfolder")
    clearing()
    
    dircheck = response["folder"]
    
                    
    if response["action"] == 'list':
    
        columns, rows = shutil.get_terminal_size()
        fileCount = 0
        filelist = globber(dircheck + "/*" + response["filter"] + '*', 'ask')

        for file in filelist:
            if os.path.isfile(file):
                fileCount = fileCount + 1
                show_file_and_metadata(str(fileCount).rjust(4, " "), file)
                
                if fileCount % (rows - 2) == 0:
                    donext = confirmation('Enter new keyword for filter, (sort), or (exit) ')
                
                    if donext == 'exit':
                        return
                    if donext == 'sort':
                        sortfolder({"folder":dircheck, "action":"sort", "filter":response["filter"]})
                        return
                    elif len(donext) > 0:
                        sortfolder({"folder":dircheck, "action":"list", "filter":donext})
                        return

        donext = confirmation('End of list.  Enter keyword for filter, single (sort) or (bulk) sorting ')
    
        if donext == 'sort':
            sortfolder({"folder":dircheck, "action":"sort", "filter":response["filter"]})
            return
        elif donext == 'bulk':

            options = {'':'./'}
            options['up'] = '../'
            options['t'] = 'trash/'
            
            if response['filter'] != '':
                options['f'] = response['filter'] + '/'
            
            where = easyoptions(options, 'Where do you want to move all these files? ')
            
            if where != '' and where != './':
                where = dircheck + '/' + where
                makenewdir(where)
            
                for file in filelist:
                    if os.path.isfile(file):
                        movefile(file, where)
                        
            return

        elif len(donext) > 0:
            sortfolder({"folder":dircheck, "action":"list", "filter":donext})
            return

    
            
            
    if response["action"] == 'sort' or response["action"] == 'sort-dirs' or response["action"] == 'quick-sort' or response["action"] == 'watch-sort':
    
        globpattern = dircheck + "/*" + response["filter"] + '*'
    
        for file in globber(globpattern, 'ask'):
        
            if os.path.isfile(file) and response["action"] == 'sort-dirs':
                continue

            if os.path.isdir(file) and (response["action"] == 'sort' or response["action"] == 'quick-sort'):
                continue

            lineitem("Filter Applied", globpattern)
            
            fresponse = sortfile(response, file)
            
            if fresponse["action"] == 'exit':
                break
            else:
                lineitem('Action', fresponse['action'])


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

    if response["action"] == 'explorer':
        print('Opening this folder in explorer...')
        os.startfile(dircheck)

    if response["action"] == 'clear':
        clear_cache()

    if response["action"] == 'melt':
            
        append = input('What do you want to append to the file names? ')
    
        for file in globber(dircheck+"/*"):
        
            if len(append) > 0:
                file = append_rename(file, append)
        
            movefile(file, pathlib.Path(file).parent.parent)



def clearing():
    print('')
    print('Switching to new screen...')
    sleep(0.5)
    os.system('cls')



def easyoptions(map, question, p_linemax = 80):

    outstring = ""

    for key in map:
        outstring = outstring + print_block('  ' + key + ' = ' + map[key])
        
        if len(outstring) >= p_linemax:
            print(outstring)
            sleep(0.01)
            outstring = ""
    
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
    
    if len(inputx) > 2:
        manylist = []
        
        for value in map.values():
            checkon = value[0:(len(inputx))]
        
            if inputx == checkon:
                lineitem('Match '+ checkon + ' on', value)
                sleep(1)
                manylist.append(value)
        
        if len(manylist) == 1:
            if affirmative_answer('Found a good match.  Do you want to use it? '):
                return manylist[0]

    input('Not a valid option: ' + inputx)

    return easyoptions(map, question, p_linemax)



def giveoptionset(sets):

    refmap = {"up":"..", "op":"open", "exit":"exit"}
    refmap["del"] = "delete"
    refmap["od"] = "open then delete"
    refmap["pl"] = "play"
    refmap["pdate"] = "push to [date]"
    
    if sets == 'root':
    
        refmap["a"] = "is actionable"
        refmap["s"] = "is someday"
        refmap["r"] = "is reference"
        refmap["c"] = "is completed"
        refmap["t"] = "is trash"
        refmap["n"] = "is not sure"
        refmap["tw"] = "to watch"
        refmap["tr"] = "to read"
        
    elif sets == '(1 tomorrow)' or sets == '(2 this week)' or sets == '(3 this month)' or sets == '(4 this quarter)' or sets == '(5 this year)' or sets == '(6 this decade)':

        refmap["pt"] = "push to (1 tomorrow)"
        refmap["pw"] = "push to (2 this week)"
        refmap["pm"] = "push to (3 this month)"
        refmap["pq"] = "push to (4 this quarter)"
        refmap["py"] = "push to (5 this year)"
        refmap["pd"] = "push to (6 this decade)"
        refmap["px"] = "push to (8 completed)"
        refmap["pz"] = "push to (9 never)"

    elif sets == 'to watch':

        refmap["d"] = "watch then delete"
        refmap["n"] = "take notes"
        refmap["ps"] = "purchase, product, or service"
        refmap["pt"] = "push to (1 tomorrow)"
        refmap["pw"] = "push to (2 this week)"
        refmap["pm"] = "push to (3 this month)"
        refmap["pq"] = "push to (4 this quarter)"
        refmap["py"] = "push to (5 this year)"
        refmap["pd"] = "push to (6 this decade)"
        refmap["px"] = "push to (8 completed)"
        refmap["pz"] = "push to (9 never)"

    elif sets == 'is actionable' or sets == 'is someday':

        refmap["h"] = "at home office"
        refmap["c"] = "at computer"
        refmap["o"] = "at outside"
        refmap["other"] = "other context"
    
    elif sets == 'at computer':

        refmap["b"] = "books"
        refmap["bo"] = "buy online"
        refmap["ed"] = "education-classes"
        refmap["e"] = "events"
        refmap["ex"] = "expert consultation"
        refmap["me"] = "find an outlet for media"
        refmap["r"] = "do web research"
        
    elif sets == 'at outside':
        
        refmap["bs"] = "buy at store"
        refmap["ed"] = "education-classes"
        refmap["e"] = "events"
        refmap["ex"] = "expert consultation"
        refmap["r"] = "restaurants"
        
    elif sets == 'at home office':
        
        refmap["pr"] = "print recipe"
        refmap["wr"] = "write to list"

    elif sets == 'priority':
    
        refmap["ps"] = "purchase, product, or service"
        refmap["lv"] = "long term value"
        refmap["h"] = "high interest"
        refmap["m"] = "medium interest"
        refmap["l"] = "low interest"
        refmap["n"] = "not sure"
        
    elif sets == 'is reference':
    
        refmap["f"] = "finances"
        refmap["l"] = "living-space"
        refmap["h"] = "health"
        refmap["p"] = "photos"
        refmap["r"] = "relationships"
        refmap["s"] = "spiritual"
        refmap["t"] = "travel"
                
    return refmap



def detectoptionset(rootoptions, file):

    currentfolder = pathlib.Path(file).parent
    
    if 'is trash' == currentfolder.stem:
        return 'done'
    elif 'is completed' == currentfolder.stem:
        return 'done'
    elif 'is not sure' == currentfolder.stem:
        return 'done'
    elif 'is reference' == currentfolder.stem:
        return 'is reference'
    elif 'is reference' == currentfolder.parent.stem:
        return 'basic'
    elif 'is reference' == currentfolder.parent.parent.stem:
        return 'basic'
    elif 'to watch' == currentfolder.parent.stem:
        return 'to watch'
    elif 'is actionable' == currentfolder.parent.stem:
        return 'is actionable'

    for key in rootoptions:
        rootfolder = rootoptions[key]
    
        if rootfolder == currentfolder.stem:
            return rootfolder
        elif rootfolder == currentfolder.parent.stem:
            return rootfolder
        elif rootfolder == currentfolder.parent.parent.stem:
            return "priority"
        elif rootfolder == currentfolder.parent.parent.parent.stem:
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
    newpath = response["folder"]
    
#   if detected == 'done':
#       return {"action": "done", "folder": response["folder"], "file": file}
    
    clearing()
    linedivider()
    show_file_and_metadata("Folder", pathlib.Path(file).parent)
    show_file_and_metadata("Sort Options For", file)
    linedivider()
    
    if response['action'] == 'quick-sort':
    
        if affirmative_answer('Is this file IMMEDIATELY actionable? '):
            gopath = 'actionable right now'
        else:
            gopath = 'non actionable'
        
        newpath = str(pathlib.Path(file).parent) + '/' + gopath
        makenewdir(newpath)
        newfilelocation = movefile(file, newpath)
        
        return {"action": "moved", "folder": newpath, "file": newfilelocation}

    elif response['action'] == 'watch-sort':
    
        if os.path.isfile(file) == False:
            return {"action": "", "folder": newpath, "file": file}
        
        if spokeninputtimeout(pathlib.Path(file).stem + ' - Do you want to play this file? ', 'n', 600, 3) == 'y':
            openfile(file)
                        
            return sortfile({"action": "sort", "folder": response["folder"]}, file)
        else:

            nowatchpath = makenewdir(response["folder"] + '/not-picked')
            newfilelocation = movefile(file, nowatchpath)
        
            return {"action": "moved", "folder": response["folder"], "file": newfilelocation}


        
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
        elif subfolder == 'play':
            openfile(newfilelocation)
            return sortfile(response, newfilelocation)
        elif subfolder == 'open then delete':
            openfile(newfilelocation)
            if affirmative_answer('Deleting ' + newfilelocation):
                os.remove(newfilelocation)
                do_log(' DEL ' + newfilelocation)

            return {"action" : "delete"}
        elif subfolder == 'delete':
            if affirmative_answer('Deleting ' + newfilelocation):
                os.remove(newfilelocation)
                do_log(' DEL ' + newfilelocation)
            
            return {"action" : "delete"}
        elif subfolder[0:4] == 'push':

            pushname = push_rename(newfilelocation, subfolder)

            return {"action" : "moved", "file": pushname}
        elif subfolder == 'exit':
            return {"action" : "exit"}

        newpath = newpath + '/' + subfolder
        
        makenewdir(newpath)
        newfilelocation = movefile(newfilelocation, newpath)
        
        return sortfile({"action": "moved", "folder": newpath}, newfilelocation)
        
    return {"action": "moved", "folder": newpath, "file": newfilelocation}

        
def explain_sleep(tx):
    print('Will wait for ' + str(tx) + ' seconds')
    sleep(tx)


def lineitem(key, value):
    columns, rows = shutil.get_terminal_size()
    linex = key.rjust(17, " ") + " | " + value
        
    print(linex[:columns])
    sleep(0.01)


def linedivider():
    lineitem("", "-------------------------------------")

def longerlineitem(key, val1, val2, val3, val4):
    lineitem(key, val1.ljust(35, " ") + val2.rjust(15, " ") + val3.rjust(15, " ") + val4.rjust(15, " "))


def confirmation(message):
    return input("*** " + message)
    

def affirmative_answer(message):
    if input(message + ' Are you sure? (y/n) ') == 'y':
        return True
    
    return False


def folderquery(message):
    entered = input(message)
    
    if entered == 'melt':
        if input('Are you sure? (y/n) ') == 'y':
            return entered
    elif entered != '':
        return entered
        
    return folderquery(message)


def makenewdir(newpath):
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        show_file_and_metadata('Created folder', newpath)
        clear_cache(pathlib.Path(newpath).parent.stem)
        
    return newpath


def openfile(filename):
    if pathlib.Path(filename).suffix.strip(".").upper() == 'URL':
        if affirmative_answer('Is this important enough to put off sorting files? '):
            explain_sleep(5)
        else:
            explain_sleep(150)
            
    os.startfile(filename)
    do_log('OPEN ' + filename)
   
   
def treecleanup(dircheck):

    items = globber(dircheck + '/*')
    
    if len(items) == 0:
        confirmation("Folder is empty and will be deleted: " + dircheck)
        os.rmdir(dircheck)
        treecleanup(str(pathlib.Path(dircheck).parent))
        
        return True
    else:
        return False
  

def movefile(current, dest):

    if pathlib.Path(current).name == 'Thumbs.db':
        os.remove(current)
        do_log(' DEL ' + current)
        return ''

    dest = str(dest) + "/" + pathlib.Path(current).name
    
    if pathlib.Path(current) == pathlib.Path(dest):
        return ''
    
    dircheck = str(pathlib.Path(current).parent)
    
    try:
        if os.path.isdir(dest):
            dest = dest + '/' + pathlib.Path(current).name + '-conflict-' + str(random.randrange(1000,9999))

        if os.path.isfile(dest):
            dest = dest + '-' + str(random.randrange(1000,9999)) + '.duplicate'

        linedivider()
        show_file_and_metadata('File to Move', current)
        show_file_and_metadata('Current', dircheck)
        os.rename(current, dest)
        show_file_and_metadata('Destination', pathlib.Path(dest).parent)
        linedivider()
        
        do_log('MOVE ' + current)
        do_log('  TO ' + dest)
        
        
        if treecleanup(dircheck):
            clear_cache(pathlib.Path(dest).parent.stem)


        
        return dest
        
    except Exception as e: 
        print(e)


# ---------------
# ---------------

os.chdir(pathlib.Path(__file__).parent)


try:
    dircheck = dirfetch('start', '.')
except:
    dircheck = input("Which drive letter to start with? ").strip()

    if dircheck == '' or dircheck == '.':
        dircheck = '.'
    else:
        dircheck = dircheck + ':'


while True:

    # debug_print("in main loop")
    
    columns, rows = shutil.get_terminal_size()
    
    try:
        response = pickfolder(dircheck, rows - 4)
        
        if response["action"] == 'exit':
            clear_cache()
            dirput('start', '.', dircheck)
            explain_sleep(2)
            break
        else:
            dircheck = response["folder"]
            
        sortfolder(response)
        
    except Exception as e:
        print(e)
        confirmation('The program has recovered from an exception')

