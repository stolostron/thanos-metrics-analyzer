
import logging
import os , shutil,datetime
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') 
logRoot = os.environ.get('LOGROOT', './logs')
logPath = logRoot+'/'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'/'

class Logger(object):

    def __init__(self,name,formatter,logPath):
        self.formatter=formatter
        self.logPath=logPath
        self.name=name
    def get_logger(self,log_file,level):
        self.createdir()
        handler = logging.FileHandler(self.logPath+log_file)        
        handler.setFormatter(self.formatter)
        Logger2 = logging.getLogger(self.name)
        Logger2.setLevel(level)
        Logger2.addHandler(handler)
        return Logger2
    def createdir(self):
        logExists = os.path.isdir(self.logPath)
        #print("Create log directory if does not exist ", self.logPath)
        if logExists == False:
            os.makedirs(self.logPath)
    def get_logPath(self):
        return self.logPath

MainLogger = Logger("main",formatter,logPath).get_logger("main.log",logging.INFO)
    
    
  


 