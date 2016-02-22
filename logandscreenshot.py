# Use:
# autoscreenshot.py [path=<path>][testcase=<testcase>][minutes=<minutes to run>|iterations=<iterations to run]
#
# Parameters can also be saved in settings.txt in the same folder
# Format: parameter=value
#
# Requirements:
# pyscreenshot, psutil ...

import pyscreenshot
import sys
import psutil
from os.path import exists
from os import mkdir
from time import strftime,sleep,clock
from multiprocessing.pool import ThreadPool


# Constants
LOG_FILE_HEADER = "pid\tname\tcpu_percent\tcreate_time\tcpu_times\tmemory_info\tmemory_percent\n"


class LogAndScreenshot():
    def __init__(self,logenabled=True, imageformat="png", filepathname="", path="", testcase="", testminutes=60*24,
                       processfilter=[]):
        self.logenabled = logenabled
        self.imageformat = imageformat
        self.filepathname = filepathname
        self.path = path
        self.testcase = testcase
        self.testminutes = testminutes
        self.iterationstotal = 60 * self.testminutes / 3
        self.processfilter = processfilter #['firefox', 'python', 'pycharm', 'EXCEL', 'taskmgr', 'explorer', 'cmd']

    def log(self, message):
        if self.logenabled:
            print(message)

    def process_args(self):
        sys.argv.pop(0)
        for arg in sys.argv:
            self.set_parameters(arg)

    def read_settings_file(self):
        try:
            f = open("settings.txt",'r')
            for line in f:
                self.set_parameters(line)
            f.close()
        except FileNotFoundError as e:
            self.log("Settings file not created. %s"%e)

    def set_parameters(self,parameter):
        # Parse parameters from command args or settings.txt
        temp = parameter.split('=')
        temp[1] = temp[1].rstrip('\n')
        if temp[0] == "path":
            self.path = temp[1]
        elif temp[0] == "testcase":
            self.testcase = temp[1]
        elif temp[0] == "minutes":
            self.testminutes = int(temp[1])
        elif temp[0] == "iterations":
            self.iterationstotal = int(temp[1])
        elif temp[0] == "filter":
            tempfilter = temp[1].split(',')
            for process in tempfilter:
                self.processfilter.append(process.strip())
        elif temp[0] == 'imageformat':
            self.imageformat = temp[1]
        else:
            self.log("Unknown parameter: %s" %(temp[0]))
            return "Unknown parameter: %s" %(temp[0])

    def iterations(self):
        # Calculate number of iterations to run
        if self.testminutes != 60 * 24:
            self.iterationstotal = self.testminutes*60 / 3
        self.log("iterationstotal: %d" %self.iterationstotal)
        return int(self.iterationstotal)

    def file_name_and_path(self):
        # Add current date and time to the name of the files
        name = strftime("%Y%m%d-%H%M%S") + "."
        self.filepathname = self.path + self.testcase
        if not exists(self.filepathname):
            mkdir(self.filepathname)
        self.filepathname += "\\" + name
        self.log("totalpath: " + self.filepathname)
        return self.filepathname

    def screenshot(self):
        # Take a screenshot and save it to file
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
    logger.read_settings_file()
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