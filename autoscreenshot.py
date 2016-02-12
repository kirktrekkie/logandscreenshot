#autoscreenshot [<path>[<folder>[<time in minutes>]]]

import pyscreenshot
import sys, os
import psutil
from time import strftime,sleep,clock
from multiprocessing.pool import ThreadPool


# Constants
LOG_FILE_HEADER = "pid\tname\tcpu_percent\tcreate_time\tcpu_times\tmemory_info\tmemory_percent\n"

class LogAndScreenshot():
    def __init__(self):
        self.logenabled = True
        self.imageformat = "jpg"
        self.filepathname = ""
        self.iterationstotal = 3600 * 24 / 3
        self.processfilter = ['firefox', 'python', 'pycharm', 'EXCEL']

    def log(self, message):
        if self.logenabled:
            print(message)

    def iterations(self):
        if len(sys.argv) == 4:
            self.iterationstotal = (int(sys.argv[3])*60 / 3)
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
        result = []
        f = open(logfile, 'w+')

        f.write('Total cpu_percent: %f' % (psutil.cpu_percent(0.2)) + '\n')
        f.write('Total memory stats: %s' % (str(psutil.virtual_memory())) + '\n\n')
        f.write(LOG_FILE_HEADER)

        pool = ThreadPool(processes=len(self.processfilter))

        for proc in psutil.process_iter():
            for pfilter in self.processfilter:
                if pfilter in proc.name():
                    result.append(pool.apply_async(self.take_out_computer_info, (proc,)))
                    #self.log(clock())
        sleep(1)
        for res in result:
            self.log("In result loop clock: %f" %(clock()))
            for info in res.get():
                self.file_writer(f,info)
            f.write('\n')
        self.log("Close file")
        f.close()

    def take_out_computer_info(self,proc):
        pinfo = [
            proc.pid,
            proc.name(),
            proc.cpu_percent(1  ),
            proc.create_time(),
            proc.cpu_times(),
            proc.memory_info(),
            proc.memory_percent()
        ]
        return pinfo

    def file_writer(self,file,info):
        if type(info) != 'str':
            info = str(info)
        file.write(info + '\t')


if(__name__ == '__main__'):
    logger = LogAndScreenshot()
    for i in range(logger.iterations()):
        start = clock()
        logger.file_name_and_path()
        logger.screenshot()
        logger.computerinfo()
        end = clock()
        logger.log("end-start: %s" %(end-start))
        if end-start < 3:
            sleep(3-(end-start))