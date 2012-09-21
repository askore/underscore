# Simple logging class.
# This module is designed to make a centralized location for all logs. It will
# be stored in the main bot object and can be accessed by different modules to
# log data in persistent manner.

#class LogStruct:
#    def __init__(fi
# TODO
#   - Make file opening more resilient.
#   - Fix args for write(...) method

import os
from datetime import datetime

class Logger:
    def __init__(self, mainLogfile):
        self.logfiles = {}
        self.logfiles["main"] = open(mainLogfile, 'a')

    def addLogfile(self, name, filepath):
        self.logfiles[name] = open(filepath, 'a')
   
    def timestamp(self):
        return datetime.today().strftime("%Y-%m-%d %H:%M:%S\t")
    
    def writeToFile(self, log = None):
        if log:
            self.logfiles[log].flush()
            os.fsync(self.logfiles[log])
        else:
            for logfile in self.logfiles:
                self.logfiles[logfile].flush()
                os.fsync(self.logfiles[logfile])

    def write(self, message, log="main", ensureWrite=False):
        message = message.strip()
        self.logfiles[log].write("%s\t%s\n" % (self.timestamp(), message))
        if ensureWrite:
            writeToFile(log)
