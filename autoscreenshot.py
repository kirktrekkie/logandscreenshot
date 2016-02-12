#autoscreenshot [<path>[<folder>[<time in minutes>]]]

import pyscreenshot
import sys, os
from time import strftime,sleep
import psutil


class LogAndScreenshot():
    def __init__(self):
        self.logenabled = True
        self.imageformat = "jpg"

    def log(self, message):
        if self.logenabled:
            print(message)

    def iterations(self):
        if len(sys.argv) == 4:
            return int(int(sys.argv[3])*60 / 2)
        else:
            return 3600 * 24

    def filename(self):
        name = strftime("%Y%m%d-%H%M%S") + ".jpg"
        if len(sys.argv) > 1:
            path = sys.argv[1]
            if len(sys.argv) > 2:
                self.log("path: " + path)
                path += "\\" + sys.argv[2]
            if not os.path.exists(path):
                os.mkdir(path)
            path += "\\" + name
            self.log("path: " + path)
            return path
        else:
            self.log("name: " + name)
            return name

    def screenshot(self, name):
        pyscreenshot.grab_to_file(name)

    def computerinfo(self):

        for proc in psutil.process_iter():
            print(proc.name())
            print(proc.cpu_percent())
            print(proc.pid)
            print(proc.create_time())
            print(proc.cpu_times())
            print(proc.memory_info())
            print(proc.memory_percent())


if(__name__ == '__main__'):
    logger = LogAndScreenshot()
    for i in range(logger.iterations()):
        path = logger.filename()
        logger.screenshot(path)
        logger.computerinfo()
        sleep(2)