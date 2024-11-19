# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 15:51:27 2024

@author: Siddh
"""
import time
from stopwatch import Stopwatch #From: https://pypi.org/project/stopwatch.py/

class Logger:
    def __init__(self, printers, decimals = 3):
        self.printingDict = {}
        self.pausedDict = {}
        self.counterDict = {}
        
        
        for p in printers:
            self.printingDict.update( {p : Stopwatch(decimals)} )
            self.pausedDict.update  ( {p : Stopwatch(decimals)} )
            self.counterDict.update ( {p : 0})
            
            self.printingDict[p].stop()
            self.printingDict[p].reset()
            
            self.pausedDict[p].stop()
            self.pausedDict[p].reset()
            
            
    def stopAllStopWatches(self):
        for printer in self.printingDict.keys():
            self.printingDict[printer].stop()
            self.pausedDict[printer].stop()
    
    
    def startAllStopWatches(self):
        for printer in self.printingDict.keys():
            self.printingDict[printer].start()
            self.pausedDict[printer].start()     
    
    
    def pauseCall(self, printer):
        self.printingDict[printer].stop()
        self.pausedDict[printer].start()
        
        self.counterDict[printer] += 1
        
    def resumeCall(self, printer):
        self.printingDict[printer].start()
        self.pausedDict[printer].stop()
    
    
    def getPrinterInfo(self, printer):
        return [float(str(self.printingDict[printer])[:-1]), float(str(self.pausedDict[printer])[:-1]), self.counterDict[printer]]
    
    def getAllPrintersInfo(self):
        ret = {}
        for printer in self.printingDict.keys():
            ret.update( {printer: self.getPrinterInfo(printer)} )
        return ret



if __name__ == "__main__":
    L = Logger(["I"])
    L.startAllStopWatches()
    time.sleep(2)
    L.pauseCall("I")
    
    print(L.getAllPrintersInfo())