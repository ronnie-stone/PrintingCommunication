# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 15:14:44 2024

@author: Siddh
"""
#Polygon Plotting
import math
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

from shapely.geometry import Polygon
from itertools import combinations
from shapely.ops import unary_union

#HTTP requests
import requests

#Envelope Management
import sys
import time

class printer:
    
    # global variable with the printer commands. Just a good way to define 
    gcode_list = {"M291": 'M291 P"Waiting for permission to continue" S3', # pauses printer to wait to be allowed to start again
                  "M292": 'M292',       # Unpauses M291 command
                  "pick": 'M23',         # Selects sd card file for printing
                  "resume": 'M24',         # Starts or Resumes Print from an sd card
                  "pause": 'M25',         # Pause a print from an sd card - runs pause.g macro.
                  "M226": 'M226',       # Never Used
                  "heat": 'M104 S250',  # Sets the extruder temperature to 250C
                  "M408": 'M408 S0'}    # Returns the status of the printer in json style. More info: https://reprap.org/wiki/G-code#M408:_Report_JSON-style_response
    
    
    def __init__ (self, OriginLocation, PrinterOffset, IP, axis, PrinterDimensions = 300, PrinterName = "p", armOneLength = 217, armTwoLength = 204):
        """
        ALL UNITS are in: mm and Radians
        Args: 
            OriginLocation: (X,Y,Theta) location of the origin of the build surface (assume the print surface is a square).
                            Theta is a rotationaltransformation applied to the rectangle allowing the printer to be rotated
            PrinterOffset: (X,Y) location of the printer base in relation to the origin
        """
        
        ##Printer Setup
        self.ax = axis
        self.PrinterName = PrinterName
        self.Point = "p"
        self.OriginLocation = OriginLocation
        self.PrinterOffset = (PrinterOffset[0], 1 * PrinterOffset[1])
        self.PrinterDimensions = PrinterDimensions
        self.IP = IP
        
        self.status = False
        self.Stored_Resume_Point = [0,0,0]
        
        self.PrinterTransformation =  transforms.Affine2D().rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2]) + self.ax.transData
        self.PrinterCoordTranslation = transforms.Affine2D().translate(self.OriginLocation[0], self.OriginLocation[1]).rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2])+ self.ax.transData
        
        self.armOneLength = armOneLength
        self.armTwoLength = armTwoLength
        
        self.scaleFactor = 5
        
        #Set up the graph of the base
        self.baseLocation = plt.plot(self.getPrinterPoint()[0], self.getPrinterPoint()[1], self.Point, transform = self.PrinterTransformation)
        self.ax.add_patch(self.getBuildSurfaceRectangle())
        
        
    """
    Printer Initialization and Plotting/Joints
    """
    def getName(self):
        return self.PrinterName
        
    def getAx(self):
        return self.ax
    
    def getBuildSurfaceRectangle(self):
        """
        Returns the print envelope of the printer as a recangle object
        """
        return plt.Rectangle((self.OriginLocation[0],self.OriginLocation[1]),
                              self.PrinterDimensions, self.PrinterDimensions , 
                              linewidth=2, edgecolor='r', facecolor='none', transform=self.PrinterTransformation)
    
    def getPrinterPoint(self):
        """
        Returns a tuple of the printer's base coordinates
        """
        return (self.OriginLocation[0] + self.PrinterOffset[0], self.OriginLocation[1] + self.PrinterOffset[1])
    
    def plotPrinterPoint(self, xyz):
        """
        Args: Takes a tuple (x,y,z)
        Plots a point using the transformation.
        """
        plt.plot(xyz[0], xyz[1], self.Point, transform = self.PrinterCoordTranslation)
    
    def getJointLocation(self, xyz, plot = False):
        """
        Args: Takes a tuple (x,y,z) of the location of the nozzle
              plot = True plots the mid joint
        Return: returns a tuple of the intermediate joint position (x, y)
        """
        x,y,z = xyz
        
        DistanceVector = (x - self.PrinterOffset[0], y - self.PrinterOffset[1])
        
        if plot:
            print(x, y, z)
            print (DistanceVector)
        
        
        a = math.sqrt(DistanceVector[0]**2 + DistanceVector[1]**2)
        b = self.armOneLength
        c = self.armTwoLength
        
        Beta = math.acos((a**2 + c**2 - b**2)/(2*a*c))
        Theta = math.atan2(DistanceVector[1], DistanceVector[0])
        
        phi = Theta-Beta
        
        if plot:
            print("\nangles")
            print("beta:  ", Beta * 180/math.pi)
            print("theta: ", Theta * 180/math.pi)
            print("phi:   ", phi * 180/math.pi)
        
        X_coord = self.armOneLength * math.cos(phi) + self.PrinterOffset[0]
        Y_coord = self.armOneLength * math.sin(phi) + self.PrinterOffset[1]
        
        location = (X_coord, Y_coord)
        
        
        base = (int(self.baseLocation[0].get_xdata()[0]), int(self.baseLocation[0].get_ydata()[0]))
        
        if plot:        
            print("\nCoordinates")
            print("Joint Location: ", location)
            print("Base Location:  ", base)
            print("End Location:   ", xyz)
        if (plot):
            self.plotPrinterPoint(location)
        
        return location
    
    
    
    """
    Polygon Creationg and plotting Functions
    """
    def getPolygonCoords(self, xyzI, xyzF, debug = False):
        """
        Args: Initial XYZ position tuple: (x, y, z),
              Final XYZ position tuple: (x, y, z)
              
        Returns: a list of the coordinates needed from the polygon.
        """
        
        JointInitial = self.getJointLocation(xyzI)
        JointFinal = self.getJointLocation(xyzF)
        NozzleInitial = (xyzI[0], xyzI[1])
        NozzleFinal = (xyzF[0], xyzF[1])
        BasePos = (int(self.baseLocation[0].get_xdata()[0]), int(self.baseLocation[0].get_ydata()[0]))
        
        polyTup = (JointInitial, NozzleInitial, NozzleFinal, JointFinal)
        
        points_array = np.array(polyTup)
        
        tf = transforms.Affine2D().translate(self.OriginLocation[0], self.OriginLocation[1])
        
        transformed_points = tf.transform(points_array)
        
        transformed_points = np.insert(transformed_points, 0, BasePos, axis = 0)
        # transformed_points = np.insert(transformed_points, 5, BasePos, axis = 0)
        
        rot = transforms.Affine2D().rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2])
        
        rotated_points = rot.transform(transformed_points)
        
        if debug:
            print(rotated_points)
            print(polyTup)
        return rotated_points
        
    def generate_all_possible_polygons(self, points):
        """
        *****INTERNAL FUNCTION*****
        Args: points = ((x1, y1), (x2, y2), (x3, y3), ... (xn, yn))
        returns: The union of all possible triangles from the given points and combine them into a single polygon.
        """
        triangles = []
        
        # Generate all combinations of exactly 3 points (triangles)
        for subset in combinations(points, 3):
            try:
                triangle = Polygon(subset)
                # Only consider valid triangles that are not self-intersecting
                if triangle.is_valid:
                    triangles.append(triangle)
            except Exception as e:
                print(f"Error creating triangle from subset {subset}: {e}")
        
        # Combine all valid triangles into a single union
        combined_polygon = unary_union(triangles)
        
        return combined_polygon
    
    
    
    def getPolygon(self, xyzI, xyzF):
        """
        *****INTERNAL FUNCTION*****
        
        Args: Initial XYZ position tuple: (x, y, z),
              Final XYZ position tuple: (x, y, z)
              
        Returns: a polygon representing the area between the 5 points
        """
        
        p = Polygon(self.getPolygonCoords(xyzI, xyzF))
        
        if (not p.is_simple):
            p = self.generate_all_possible_polygons((self.getPolygonCoords(xyzI, xyzF)))
        
        
        return p
    
    def getScaledPolygon(self, xyzI, xyzF):
        """
        Args: Initial XYZ position tuple: (x, y, z),
              Final XYZ position tuple: (x, y, z)
              
        Returns: Scaled up polygon from the getPolygon to apply a border condition to the function
        """
        
        p = self.getPolygon(xyzI, xyzF)
        scaled = p.buffer(self.scaleFactor)
        
        return scaled
    
    def getLiveAnalysisPolygon(self):
        """
        wrapper for the scaled polygon method that thakes inputs of the printer's actual coordinates through HTTP
        """
        
        return self.getScaledPolygon(self.getCurrentPosition(), self.getTargetPosition())
    
    def plot(self, ax):
        """
        plots the printer 
        """
        locationI = self.getCurrentPosition()
        locationF = self.getTargetPosition()
        
        self.plotPrinterPoint(locationI)
        self.getJointLocation(locationI)
        
        self.plotPrinterPoint(locationF)
        self.getJointLocation(locationF)
        
        polygon1 = self.getScaledPolygon(locationI, locationF)
        
        x, y = polygon1.exterior.xy
        
        self.ax.fill(x, y, alpha=0.5, fc='red', label= self.PrinterName)

    
    """
    Printer Network Functions
    """
    def getTargetPosition(self):
        """
        This is for getting the target end position from the printer
        """
        
        #Status false means the printer is paused. Otherwise it just return the target position
        if self.status == False:
            return self.Stored_Resume_Point
        else:
            # return self.request_status()["coords"]["xyz"]
            return (0,300,0)
        
    
    def getCurrentPosition(self):
        """
        This is for getting the current position from the printer
        """
        # return self.request_status()["coords"]["machine"]
        return (300,300,0)
    
    def request_status(self):
    	base_request = ("http://{0}:{1}/rr_status?type=0").format(self.IP,"")
    	return requests.get(base_request).json()
    
    def issue_gcode(self, com, filename=""):
        base_request = ("http://{0}:{1}/rr_gcode?gcode=" + self.gcode_list[com] + filename).format(self.IP,"")
        r = requests.get(base_request)
        return r
    
    def pause(self):
        self.Stored_Resume_Point = self.getCurrentPosition()
        self.issue_gcode("pause")
        self.status = False
        
    def resume(self):
        self.Stored_Resume_Point = []
        self.issue_gcode("resume")
        self.status = True
        
    def pickFile(self, filename):
        self.issue_gcode("pick", filename)
    
    def preheat(self):
        self.issue_gcode("heat")
        
    def getStatus(self):
        return self.status
        
    
        
class envelope:
    def __init__(self, printers):
        """
        printers is either a 2D list with the parameters to create a printer in the order:
            [Origin location (x,y,theta), Base offset (x, y), "ip address", "Printer Name"]
            
        or printers is a list of printer objects:
            [Printer1, Printer2, Printer3]
        """
        try:
            printers[0][0]
            
            self.fig, self.ax = plt.subplots()
            
            self.printerList = []
            for details in printers:
                self.printerList.append(printer(details[0], details[1], details[2], self.ax, PrinterName = details[3]))
            
            
            
            
            minX = self.getMinMaxX()[0]
            maxX = self.getMinMaxX()[1]
            
            minY = self.getMinMaxY()[0]
            maxY = self.getMinMaxY()[1]
            
            
            # print(minX, maxX, "\n")
            
            # print(minY, maxY)
            
            
            self.ax.set_xlim(minX-150, maxX)
            self.ax.set_ylim(minY-150, maxY)
            
            # plt.show()
        except:
            print("alt")
            self.alt__init__(printers)
        
        
    def alt__init__(self, printers):
        
        
        self.printerList = printers
        
        self.ax = self.printerList[0].getAx()
        
        
        minX = self.getMinMaxX()[0]
        maxX = self.getMinMaxX()[1]
        
        minY = self.getMinMaxY()[0]
        maxY = self.getMinMaxY()[1]
        
        
        # print(minX, maxX, "\n")
        # print(minY, maxY)
        
        
        self.ax.set_xlim(minX-30, maxX+30)
        self.ax.set_ylim(minY-150, maxY+150)
        
        # plt.show()
    
    def getMinMaxX(self):
        """
        *****INTERNAL FUNCTION*****
        Used to get the X minimum and X maximum values for the printer workspace
        """
        
        minX = sys.maxsize
        maxX = -1*sys.maxsize
        
        for printer in self.printerList:
            printerRect = printer.getBuildSurfaceRectangle()
            LeftX = printerRect.get_xy()[0]
            RightX = printerRect.get_xy()[0] + printerRect.get_width()
            
            if(LeftX < minX):
                minX = LeftX
            
            if(RightX > maxX):
                maxX = RightX
        
        return(minX, maxX)
    
    def getMinMaxY(self):
        """
        *****INTERNAL FUNCTION*****
        Used to get the Y minimum and Y maximum values for the printer workspace
        """
        
        minY = sys.maxsize
        maxY = -1*sys.maxsize
        
        for printer in self.printerList:
            printerRect = printer.getBuildSurfaceRectangle()
            LowerY = printerRect.get_xy()[1]
            UpperY = printerRect.get_xy()[1] + printerRect.get_height()
            
            if(LowerY < minY):
                minY = LowerY
            
            if(UpperY > maxY):
                maxY = UpperY
        
        return(minY, maxY)
    
    
    def plotAll(self):
        """
        plots all the printers
        """
        for pr in self.printerList:
            pr.plot(self.ax)
    
    def getIntersections(self):
        """
        FINISH IMPLEMENTATION
        Determines the interesctions between all of the polygons from the printer motion.
        """
        intersectionList = []
        
        for printer1 in self.printerList.copy():
            
            otherPs = self.printerList.copy()
            otherPs.remove(printer1)
            
            poly1 = printer1.getLiveAnalysisPolygon()
            
            
            for printer2 in otherPs: # iterate through all the other printers
                poly2 = printer2.getLiveAnalysisPolygon() #get the polygon from the printer
                
                if poly1.intersects(poly2) and (printer1 not in intersectionList) and (printer2 not in intersectionList):
                    intersectionList.append(printer2)
                    
        
        
        
        for a in intersectionList:
            print(a.getName())
        return intersectionList
    
    def prepare(self, filename = ""):
        """
        Filename assumes that the files on the printers are in the format "filename_(number)"
        number is the printer's number in reference to the list which was used to initialize the printers
        """
        for i in range(len(self.printerList)):
            pr = self.printerList[i]
            pr.preheat()
            pr.pickFile(filename +"_"+str(i))
            
    def startPrints(self):
        """
        Should be be run to start the prints at the same time.
        Need to make sure the hotends are warm before this runs though
        """
        for pr in self.printerList:
            pr.resume()
            
    def checkingAlgorithm(self):
        """
        Need to test this method, but it should work...
        """
        intersectionList = self.getIntersections()
        for pr in intersectionList:
            pr.pause()
            
        intersectionList = self.getIntersections()
        for pr in self.printerList():
            if pr.getStatus() == False and pr not in intersectionList:
                pr.resume()
                    
            
if __name__ == "__main__":
    
    # fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()
    
    # ax2.set_xlim(-200, 1000)
    # ax2.set_ylim(-100, 1000)
    
    p = printer((0,0,0), (150, -35), "192.168.0.17", ax2, PrinterName = "printer 1")
    p.plot(ax2)
    
    # print(p.getLocations((0,0,0)))
    
    locationI = (300,300,0)
    locationF = (0,300,0)
    
    # p.plot(ax2)
    
    # p.plotPrinterPoint(locationI)
    # p.getJointLocation(locationI)
    
    # p.plotPrinterPoint(locationF)
    # p.getJointLocation(locationF)
    
    # # polygon1 = p.getPolygon(locationI, locationF)
    
    # polygon2 = p.getScaledPolygon(locationI, locationF)
    
    # # x1, y1 = polygon1.exterior.xy
    
    # x2, y2 = polygon2.exterior.xy
    
    
    # # ax.fill(x1, y1, alpha=0.5, fc='blue', label='Polygon 1')
    
    # ax2.fill(x2, y2, alpha=0.5, fc='red', label='Polygon 2')
    # p.plot()
    
    
    
    p2 = printer((0,600,270), (150, -35), "IP3", ax2, PrinterName = "printer 2")
    p2.plot(ax2)
    # p2.plot(ax2)
    # print(p.getLocations((0,0,0)))
    
    # locationI2 = (300,300,0)
    # locationF2 = (0,300,0)
    
    # p2.plotPrinterPoint(locationI2)
    # p2.getJointLocation(locationI2, True)
    
    # p2.plotPrinterPoint(locationF2)
    # p2.getJointLocation(locationF2, True)
    
    # # Poly1 = p2.getPolygon(locationI2, locationF2)
    
    # Poly2 = p2.getScaledPolygon(locationI2, locationF2)
    
    # # x3, y3 = Poly1.exterior.xy
    
    # x4, y4 = Poly2.exterior.xy
    
    
    # # ax.fill(x3, y3, alpha=0.5, fc='blue', label='P1 1')
    
    # ax2.fill(x4, y4, alpha=0.5, fc='red', label='P2 2')
    
    
    
    p3 = printer((300,900,180), (150, -35), "IP3", ax2, PrinterName = "printer 3")
    p3.plot(ax2)
    # print(p.getLocations((0,0,0)))
    
    # locationI2 = (300,300,0)
    # locationF2 = (0,300,0)
    
    # p3.plotPrinterPoint(locationI2)
    # p3.getJointLocation(locationI2, True)
    
    # p3.plotPrinterPoint(locationF2)
    # p3.getJointLocation(locationF2, True)
    
    # # Poly1 = p2.getPolygon(locationI2, locationF2)
    
    # Poly3 = p3.getScaledPolygon(locationI2, locationF2)
    
    # # x3, y3 = Poly1.exterior.xy
    
    # x5, y5 = Poly3.exterior.xy
    
    
    # # ax.fill(x3, y3, alpha=0.5, fc='blue', label='P1 1')
    
    # ax2.fill(x5, y5, alpha=0.5, fc='red', label='P2 2')

    # plt.show()
    # plt.show()
    
    
    
    """
    Full Envelope testing
    """
    e = envelope([p, p2, p3])
    e.getIntersections()
    
    
    # printers = [[(0,0,0), (150, -35), "IP1", "Printer 1"],
    #             [(0,600,270), (150, -35), "IP2", "Printer 2"],
    #             [(300,900,180), (150, -35), "IP3", "Printer 3"]]
    # e = envelope(printers)
    
    # # for i in range(100):
    # e.plotAll()
    
    
    # start_time = time.time()
    
    # for i in range(1000):
    #     e.getIntersections()
    
    # end_time = time.time()

    # runtime = (end_time - start_time)/1000

    # print(f"Runtime: {runtime} seconds")

    
    
    

