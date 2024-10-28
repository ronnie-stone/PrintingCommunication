# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:16:28 2024

@author: Siddh
"""

import requests
import math


import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.affinity import scale


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
        @Args:
            ip: String of the ip address of the printer
            fileName: file that you want to print
            location: the position of (0,0,0) in the total print envelope ****Need to learn more about this
            ArmOneLength: Should be constant but can be changed for different printers
            ArmTwoLength: Should be constant but can be changed for different printers
        
        """
        self.XOFFSETFROMZERO = 150  #mm
        self.YOFFSETFROMZERO = -30   #mm
        
        ###Length of the arms in milimeters
        self.armOneLength = armOneLength                                # The thicker joint on the printer (first one)
        self.armTwoLength = armTwoLength                                # The thinner joint on the printer (second one)
        
        self.ip = ip
        self.fileName = fileName
        self.baseLocation = location # list of x,y coords
        
        
        self.targetCoords = self.request_status()['xyz']                # Gets the target list of the x, y, z coords of the printer
        self.currentCoords = self.request_status()['coords']            # Gets the current list of the x, y, z coords of the printer
        
        self.targetThetas = self.findJointAngles(self.targetCoords)     # gets the target angles in radians
        self.currentThetas = self.findJointAngles(self.currentCoords)   # gets the current angles in radians
        
        self.targetJointLocations = []
        self.currentJointLocations = []
        
        self.update()
        
        """0 implies that the arm is homed"""
        #self.jointOneDegrees = 0 # Joint one is the primary joint       Range of values should be (0, 170) - 0 is homed 170 is full extension
        #self.jointTwoDegrees = 0 # Joint two is the second joint        Range of values should be (0,164)  - 0 is homed 164 is full extension
        
        
        
    """Getter Methods"""
    def getJointDegrees(self):
        return [self.jointOneDegrees, self.jointTwoDegrees]
    
    def getIP(self):
        return self.ip
    
    def getBaseLocation(self):
        return self.baseLocation
    
    def getJointAngles(self):
        return [self.jointOneDegrees, self.jointTwoDegrees]
    
    def getPolygonCoords(self):
        retLis = [self.getBaseLocation()[:2]]
        
        for i in self.currentJointLocations:
            retLis.append(i)
        for i in self.targetJointLocations:
            retLis.append(i)
        retLis.append(self.getBaseLocation()[:2])
        
        print("\n\nPolygon Coords")
        print(retLis)
        return retLis
    
    def getInfo(self):
        print("Target first and then current")
        print("XYZ")
        print(self.targetCoords)
        print(self.currentCoords)
        
        print("\nAngles")
        print(self.targetThetas)
        print(self.currentThetas)
        
        print("\nJoint Locations")
        print(self.targetJointLocations)
        print(self.currentJointLocations)
        
        
        
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
        
        ArmOneAngle = math.acos((d**2  - self.armOneLength**2 - self.armTwoLength**2) / (2 * self.armOneLength * self.armTwoLength))
        
        alpha = math.atan(y/x)
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
        self.currentCoords = self.request_status()['coords']
        
    def updateAngles(self):
        """updates the theta angles based on the xyz coordinates"""
        self.targetThetas = self.findJointAngles(self.targetCoords)
        self.currentThetas = self.findJointAngles(self.currentCoords)
    
    def updateJointLocations(self):
        self.targetJointLocations = self.findJointLocations(self.targetCoords)
        self.currentJointLocations = self.findJointLocations(self.currentCoords)
    
    def update(self):
        """User FACING METHOD"""
        self.updateXYZ()
        self.updateAngles()
        self.updateJointLocations()
    
    
    """Printer Functions"""
    def request_status(self):
    	#base_request = ("http://{0}:{1}/rr_status?type=0").format(self.ip,"")
    	return {"xyz": [1,0.5,0], "coords":[1,1,0]}
    
    def issue_gcode(self, com, filename=""):
    	base_request = ("http://{0}:{1}/rr_gcode?gcode=" + self.gcode_list[com] + self.filename).format(self.ip,"")
    	r = requests.get(base_request)
    	return r    
        
    
    
    
    
    
    
    
#Test the Code    
if __name__ == "__main__":
    P1 = printer("123.345.0.2","Test.gcode",[120,3,4])
    P1.getInfo()
    
    # polygon1_coords = P1.getPolygonCoords()
    
    # polygon1 = Polygon(polygon1_coords)
    
    # fig, ax = plt.subplots()
    
    # x1, y1 = polygon1.exterior.xy
    
    # ax.fill(x1, y1, alpha=0.5, fc='blue', label='Polygon 1')
    
    # ax.legend()
    # plt.show()
    





