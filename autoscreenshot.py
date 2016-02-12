#autoscreenshot [<path>[<folder>[<time in minutes>]]]

import pyscreenshot
import sys, os
from time import strftime,sleep
import psutil


class LogAndScreenshot():
    def __init__(self):
        self.logenabled = True
        self.imageformat = "jpg"
        self.filepathname = ""
        self.iterationstotal = 3600 * 24

    def log(self, message):
        if self.logenabled:
            print(message)

    def iterations(self):
        if len(sys.argv) == 4:
            self.iterationstotal = (int(sys.argv[3])*60 / 2)
        return int(self.iterationstotal)

    def file_name_and_path(self):
        name = strftime("%Y%m%d-%H%M%S") + "."
        if len(sys.argv) > 1:
            path = sys.argv[1]
            if len(sys.argv) > 2:
                self.log("path: " + path)
                path += "\\" + sys.argv[2]
            if not os.path.exists(path):
                os.mkdir(path)
            self.filepathname = path + "\\" + name
            self.log("path: " + path)
            return path
        else:
            self.log("name: " + name)
            self.filepathname = name
            return name

    def screenshot(self):
        name = self.filepathname + self.imageformat
        pyscreenshot.grab_to_file(name)

    def computerinfo(self):
        logfile = self.filepathname + "log"
        f = open(logfile, 'w+')
        for proc in psutil.process_iter():
            self.file_writer(f,proc.pid)
            self.file_writer(f,proc.name())
            self.file_writer(f,proc.cpu_percent())
            self.file_writer(f,proc.create_time())
            self.file_writer(f,proc.cpu_times())
            self.file_writer(f,proc.memory_info())
            self.file_writer(f,proc.memory_percent())
            f.write('\n')
        f.close()

    def file_writer(self,file,info):
        if type(info) != 'str':
            info = str(info)
        file.write(info + '\t')


if(__name__ == '__main__'):
    logger = LogAndScreenshot()
    for i in range(logger.iterations()):
        logger.file_name_and_path()
        logger.screenshot()
        logger.computerinfo()
        sleep(2)