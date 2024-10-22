# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 15:16:50 2024

@author: Siddh
"""
import requests

class printer:
    gcode_list = {"M291": 'M291 P"Waiting for permission to continue" S3', # pauses printer to wait to be allowed to start again
                  "M292": 'M292',       # Unpauses M291 command
                  "M23": 'M23',         # Selects sd card file for printing
                  "M24": 'M24',         # Starts or Resumes Print from an sd card
                  "M25": 'M25',         # Pause a print from an sd card - runs pause.g macro.
                  "M226": 'M226',       # Never Used
                  "M104": 'M104 S240',  # Sets the extruder temperature to 240C
                  "M408": 'M408 S0'}    # Returns the status of the printer in json style. More info: https://reprap.org/wiki/G-code#M408:_Report_JSON-style_response
    
    def __init__(self, ip, fileName, location, armOneLength = 217, armTwoLength = 204):
        self.ip = ip
        self.fileName = fileName
        self.baseLocation = location
        
        self.targetCoords = self.request_status()['xyz']
        self.currentCoords = self.request_status()['coords']

        
        """0 implies that the arm is homed"""
        self.jointOneDegrees = 0 # Joint one is the primary joint       Range of values should ne (0, 170)
        self.jointTwoDegrees = 0 # Joint two is the second joint        Range of values should be (0,164)
        
        """Length of the arms in milimeters"""
        self.armOneLength = armOneLength                                # The thicker joint on the printer (first one)
        self.armTwoLength = armTwoLength                                # The thinner joint on the printer (second one)
    
        
    """Getter Methods"""
    def getJointDegrees(self):
        return [self.jointOneDegrees, self.jointTwoDegrees]
    
    def getIP(self):
        return self.ip
    
    def getBaseLocation(self):
        return self.baseLocation
    
    """Actual Stuff"""
    def request_status(self):
    	base_request = ("http://{0}:{1}/rr_status?type=0").format(self.ip,"")
    	return requests.get(base_request).json()
    
    def issue_gcode(self, com, filename=""):
    	base_request = ("http://{0}:{1}/rr_gcode?gcode=" + self.gcode_list[com] + self.filename).format(self.ip,"")
    	r = requests.get(base_request)
    	return r
    
    def updateXYZ(self):
        """ Updates the XYZ list as an HTTP request"""
        self.targetCoords = self.request_status()['xyz']
        self.currentCoords = self.request_status()['machine']
        
    
    
        
        
        