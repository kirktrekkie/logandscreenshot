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
        self.path = ""
        self.testcase = ""
        self.testminutes = 60 * 24
        self.iterationstotal = 60 * self.testminutes / 3
        self.processfilter = [] #['firefox', 'python', 'pycharm', 'EXCEL', 'taskmgr', 'explorer', 'OneDrive', 'cmd']

    def log(self, message):
        if self.logenabled:
            print(message)

    def process_args(self):
        sys.argv.pop(0)
        for arg in sys.argv:
            temp = arg.split('=')
            if temp[0] == "path":
                self.path = temp[1]
            elif temp[0] == "testcase":
                self.testcase = temp[1]
            elif temp[0] == "minutes":
                self.testminutes = int(temp[1])
            elif temp[0] == "iterations":
                self.iterationstotal = int(temp[1])

            else:
                self.log("Unknown parameter: %s" %(temp[0]))

    def iterations(self):
        if self.testminutes != 60 * 24:
            self.iterationstotal = self.testminutes*60 / 3
        self.log("iterationstotal: %d" %self.iterationstotal)
        return int(self.iterationstotal)

    def file_name_and_path(self):
        name = strftime("%Y%m%d-%H%M%S") + "."
        self.filepathname = self.path + self.testcase
        if not os.path.exists(self.filepathname):
            os.mkdir(self.filepathname)
        self.filepathname += "\\" + name
        self.log("totalpath: " + self.filepathname)
        return self.filepathname

    def screenshot(self):
        name = self.filepathname + self.imageformat
        pyscreenshot.grab_to_file(name)

    def computerinfo(self):
        logfile = self.filepathname + "log"
        # Use threads to take out cpu_percent for the different processes
        result = []
        # No filter
        if len(self.processfilter) == 0:
            numproc = len(psutil.pids())
            print(numproc)
            pool = ThreadPool(processes=numproc)
            for proc in psutil.process_iter():
                result.append(pool.apply_async(self.take_out_computer_info, (proc,)))
        # With filter
        else:
            pool = ThreadPool(processes=len(self.processfilter))
            for proc in psutil.process_iter():
                for pfilter in self.processfilter:
                    if pfilter in proc.name():
                        result.append(pool.apply_async(self.take_out_computer_info, (proc,)))
                        break
                        #self.log(clock())

        # While threads are running take out total cpu_percent and start write to file
        f = open(logfile, 'w+')
        f.write('Total cpu_percent: %f' % (psutil.cpu_percent(1)) + '\n')
        f.write('Total memory stats: %s' % (str(psutil.virtual_memory())) + '\n\n')
        f.write(LOG_FILE_HEADER)
        #sleep(1)

        # Get the results from the threads and write them to file
        for res in result:
            try:
                #self.log("In result loop clock: %f" %(clock()))
                for info in res.get():
                    self.file_writer(f,info)
            except (ProcessLookupError, psutil.NoSuchProcess) as e:
                self.log("Process not found. %s" %e)
            f.write('\n')
        self.log("Close file")
        pool.close()
        pool.terminate()
        pool.join()
        f.close()

    def take_out_computer_info(self,proc):
        try:
            pinfo = [
                proc.pid,
                proc.name(),
                proc.cpu_percent(1),
                proc.create_time(),
                proc.cpu_times(),
                proc.memory_info(),
                proc.memory_percent()
            ]
            return pinfo
        except ProcessLookupError as e:
            self.log("Process not found. %s" %e)

    def file_writer(self,file,info):
        if type(info) != 'str':
            info = str(info)
        file.write(info + '\t')


if __name__ == '__main__':
    logger = LogAndScreenshot()
    logger.process_args()
    for i in range(logger.iterations()):
        logger.log("iteration: %d"%i)
        start = clock()
        logger.file_name_and_path()
        logger.screenshot()
        logger.computerinfo()
        end = clock()
        logger.log("end-start: %s" %(end-start))
        if end-start < 3:
            sleep(3-(end-start))