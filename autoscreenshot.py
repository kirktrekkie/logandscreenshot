#autoscreenshot [<path>[<folder>[<time in minutes>]]]

import pyscreenshot
import sys, os
from time import strftime,sleep

logenabled = True


def log(message):
    if logenabled:
        print(message)


def iterations():
    if len(sys.argv) == 4:
        return int(int(sys.argv[3])*60 / 2)
    else:
        return 3600 * 24


def filename():
    name = strftime("%Y%m%d-%H%M%S") + ".jpg"
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if len(sys.argv) > 2:
            log("path: " + path)
            path += "\\" + sys.argv[2]
        if not os.path.exists(path):
            os.mkdir(path)
        path += "\\" + name
        log("path: " + path)
        return path
    else:
        log("name: " + name)
        return name


def screenshot(name):
    pyscreenshot.grab_to_file(name)


if(__name__ == '__main__'):
    for i in range(iterations()):
        path = filename()
        screenshot(path)
        sleep(2)