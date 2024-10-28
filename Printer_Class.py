# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 15:16:50 2024

@author: Siddh
"""
import requests
import shapely
import math

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
        
        """
        Inputs:
            ip: String of the ip address of the printer
            fileName: file that you want to print
            location: the position of the printer in the build Envelop ****Need to learn more about this
            ArmOneLength: Should be constant but can be changed for different printers
            ArmTwoLength: Should be constant but can be changed for different printers
        """
        self.XOFFSETFROMZERO = 150  #mm
        self.YOFFSETFROMZERO = -30   #mm
        
        self.ip = ip
        self.fileName = fileName
        self.baseLocation = location # list of x,y coords
        
        
        self.targetCoords = self.request_status()['xyz']                # Gets the target list of the x, y, z coords of the printer
        self.currentCoords = self.request_status()['coords']            # Gets the current list of the x, y, z coords of the printer
        
        self.targetThetas = self.findJointAngles(self.targetCoords)     # gets the target angles in radians
        self.currentThetas = self.findJointAngles(self.currentCoords)   # gets the current angles in radians
        
        """0 implies that the arm is homed"""
        #self.jointOneDegrees = 0 # Joint one is the primary joint       Range of values should be (0, 170) - 0 is homed 170 is full extension
        #self.jointTwoDegrees = 0 # Joint two is the second joint        Range of values should be (0,164)  - 0 is homed 164 is full extension
        
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
    
    def getJointAngles(self):
        return [self.jointOneDegrees, self.jointTwoDegrees]
    
    """Background Math Stuff"""
    def findJointAngles(self, xyz):
        """
        Input: List with the XYZ coordinates
        Output: Tuple in the format (Arm one Angle, Arm two Angle)
        NOTE: This may not correspond to the actual printer's angles.
        """
        x = xyz[0] + self.XOFFSETFROMZERO
        y = xyz[1] + self.YOFFSETFROMZERO
        
        d = (x**2 + y**2)**0.5
        
        ArmOneAngle = math.acos((d^2  - self.armOneLength**2 - self.armTwoLength**2) / (2 * self.armOneLength * self.armTwoLength))
        
        alpha = math.arcTan(y/x)
        beta = math.acos((self.armOneLength**2 + d**2 - self.armTwoLength**2) / (2* self.armOneLength * d))
        
        ArmTwoAngle = alpha - beta
                
        return (ArmOneAngle, ArmTwoAngle) # Returns a value in radians
    
    def findJointLocations(self, xyz):
        """
        Input: List with the XYZ coordinates
        Output: 2D tuples - (Elbow Position (x,y), End Position (x,y))
        """
        x = xyz[0]
        y = xyz[1]
        theta = self.findJointAngles(xyz)[0]
        
        ElbowPosition = (self.armOneLength * math.cos(theta), self.armOneLength * math.sin(theta))
        EndPosition = (x,y)
        
        return (ElbowPosition, EndPosition)
    
    
    
    """Periodic Requests"""
    def updateXYZ(self):
        """ Updates the XYZ list as an HTTP request"""
        self.targetCoords = self.request_status()['xyz']
        self.currentCoords = self.request_status()['machine']
        
    def updateAngles(self):
        """updates the theta angles based on the xyz coordinates"""
        self.targetThetas = self.findJointAngles(self.targetCoords)
        self.currentThetas = self.findJointAngles(self.currentCoords)
        
    def update(self):
        """User FACING METHOD"""
        self.updateXYZ()
        self.updateAngles()
    
    
    
    """Printer Functions"""
    def request_status(self):
    	base_request = ("http://{0}:{1}/rr_status?type=0").format(self.ip,"")
    	return requests.get(base_request).json()
    
    def issue_gcode(self, com, filename=""):
    	base_request = ("http://{0}:{1}/rr_gcode?gcode=" + self.gcode_list[com] + self.filename).format(self.ip,"")
    	r = requests.get(base_request)
    	return r    
        
        