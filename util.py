import os
import shutil

def clear():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
  
    # for mac and linux (here, os.name is 'posix')
    else:
        _ = os.system('clear')

def divider():
    count = int(shutil.get_terminal_size().columns)
    count = count - 1
    print('-' * count)

def formatSeconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return "%02d:%02d:%02d" % (hours, minutes, seconds)
