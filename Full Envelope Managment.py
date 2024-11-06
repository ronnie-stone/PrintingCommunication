# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 15:14:44 2024

@author: Siddh
"""
import math
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

#Polygon Plotting
import numpy as np
from shapely.geometry import Polygon
from itertools import combinations
from shapely.ops import unary_union

#HTTP requests
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
    def __init__ (self, OriginLocation, PrinterOffset, IP, ax, PrinterDimensions = 300, PrinterName = "p", armOneLength = 217, armTwoLength = 204):
        """
        ALL UNITS are in: mm and Radians
        Args: 
            OriginLocation: (X,Y,Theta) location of the origin of the build surface (assume the print surface is a square).
                            Theta is a rotationaltransformation applied to the rectangle allowing the printer to be rotated
            PrinterOffset: (X,Y) location of the printer base in relation to the origin
        """
        
        ##Printer Setup
        self.Name = PrinterName
        self.OriginLocation = OriginLocation
        self.PrinterOffset = (PrinterOffset[0], 1 * PrinterOffset[1])
        self.PrinterDimensions = PrinterDimensions
        self.IP = IP
        
        self.PrinterTransformation =  transforms.Affine2D().rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2]) + ax.transData
        self.PrinterCoordTranslation = transforms.Affine2D().translate(self.OriginLocation[0], self.OriginLocation[1]).rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2])+ ax.transData
        
        self.armOneLength = armOneLength
        self.armTwoLength = armTwoLength
        
        self.scaleFactor = 5
        
        #Set up the graph of the base
        self.baseLocation = plt.plot(self.getPrinterPoint()[0], self.getPrinterPoint()[1], self.Name, transform = self.PrinterTransformation)
        ax.add_patch(self.getBuildSurfaceRectangle())
        
        
    """
    Printer Initialization and Plotting/Joints
    """
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
        plt.plot(xyz[0], xyz[1], self.Name, transform = self.PrinterCoordTranslation)
    
    def getJointLocation(self, xyz, plot = False):
        """
        Args: Takes a tuple (x,y,z) of the location of the nozzle
              plot = True plots the mid joint
        Return: returns a tuple of the intermediate joint position (x, y)
        """
        x,y,z = xyz
        
        DistanceVector = (x - self.PrinterOffset[0], y - self.PrinterOffset[1])
        
        print(x, y, z)
        print (DistanceVector)
        
        
        a = math.sqrt(DistanceVector[0]**2 + DistanceVector[1]**2)
        b = self.armOneLength
        c = self.armTwoLength
        
        Beta = math.acos((a**2 + c**2 - b**2)/(2*a*c))
        Theta = math.atan2(DistanceVector[1], DistanceVector[0])
        
        phi = Theta-Beta
        
        print("\nangles")
        print("beta:  ", Beta * 180/math.pi)
        print("theta: ", Theta * 180/math.pi)
        print("phi:   ", phi * 180/math.pi)
        
        X_coord = self.armOneLength * math.cos(phi) + self.PrinterOffset[0]
        Y_coord = self.armOneLength * math.sin(phi) + self.PrinterOffset[1]
        
        location = (X_coord, Y_coord)
        
        
        base = (int(self.baseLocation[0].get_xdata()[0]), int(self.baseLocation[0].get_ydata()[0]))
        
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
    def getPolygonCoords(self, xyzI, xyzF):
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
    
    def getScaledPolygon(self, xyzI, xyzF):
        """
        Args: Initial XYZ position tuple: (x, y, z),
              Final XYZ position tuple: (x, y, z)
              
        Returns: Scaled up polygon from the getPolygon to apply a border condition to the function
        """
        
        p = self.getPolygon(xyzI, xyzF)
        scaled = p.buffer(self.scaleFactor)
        
        return scaled
    
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
    
    def plot(self):
        pass

    
    """
    Printer Network Functions
    """
    def getTargetPosition(self):
        """
        Implement eventually. This one is for getting the end position from the printer
        """
        return(0,0,0)
    
    def getCurrentPosition(self):
        """
        Implement eventually. This one is for getting the current position from the printer
        """
        return(0,0,0)
    
    def request_status(self):
    	base_request = ("http://{0}:{1}/rr_status?type=0").format(self.IP,"")
    	return requests.get(base_request).json()
    
    def issue_gcode(self, com, filename=""):
    	base_request = ("http://{0}:{1}/rr_gcode?gcode=" + self.gcode_list[com] + self.filename).format(self.IP,"")
    	r = requests.get(base_request)
    	return r
        
        
        
class envelope:
    def __init__(self, printers):
        self.fig, self.ax = plt.subplots()
        self.printerList = printers
        
        minX = self.getMinMaxX()[0]
        maxX = self.getMinMaxX()[1]
        
        minY = self.getMinMaxY()[0]
        maxY = self.getMinMaxY()[1]
        
        self.ax.set_xlim(minX, maxX)
        self.ax.set_ylim(minY, maxY)
        
        plt.show()

    def getMinMaxX(self):
        pass
    def getMinMaxY(self):
        pass
    
    
if __name__ == "__main__":
    # e = envelope([])
    
    # fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()
    
    ax2.set_xlim(-200, 1000)
    ax2.set_ylim(-100, 1000)
    
    p = printer((0,0,0), (150, -35), "IP3", ax2)
    
    # print(p.getLocations((0,0,0)))
    
    locationI = (300,300,0)
    locationF = (0,300,0)
    
    p.plotPrinterPoint(locationI)
    p.getJointLocation(locationI)
    
    p.plotPrinterPoint(locationF)
    p.getJointLocation(locationF)
    
    # polygon1 = p.getPolygon(locationI, locationF)
    
    polygon2 = p.getScaledPolygon(locationI, locationF)
    
    # x1, y1 = polygon1.exterior.xy
    
    x2, y2 = polygon2.exterior.xy
    
    
    # ax.fill(x1, y1, alpha=0.5, fc='blue', label='Polygon 1')
    
    ax2.fill(x2, y2, alpha=0.5, fc='red', label='Polygon 2')
    
    
    
    
    p2 = printer((0,600,270), (150, -35), "IP3", ax2)
    
    # print(p.getLocations((0,0,0)))
    
    locationI2 = (300,300,0)
    locationF2 = (0,300,0)
    
    p2.plotPrinterPoint(locationI2)
    p2.getJointLocation(locationI2, True)
    
    p2.plotPrinterPoint(locationF2)
    p2.getJointLocation(locationF2, True)
    
    # Poly1 = p2.getPolygon(locationI2, locationF2)
    
    Poly2 = p2.getScaledPolygon(locationI2, locationF2)
    
    # x3, y3 = Poly1.exterior.xy
    
    x4, y4 = Poly2.exterior.xy
    
    
    # ax.fill(x3, y3, alpha=0.5, fc='blue', label='P1 1')
    
    ax2.fill(x4, y4, alpha=0.5, fc='red', label='P2 2')
    
    
    
    p3 = printer((300,900,180), (150, -35), "IP3", ax2)
    
    # print(p.getLocations((0,0,0)))
    
    locationI2 = (300,300,0)
    locationF2 = (0,300,0)
    
    p3.plotPrinterPoint(locationI2)
    p3.getJointLocation(locationI2, True)
    
    p3.plotPrinterPoint(locationF2)
    p3.getJointLocation(locationF2, True)
    
    # Poly1 = p2.getPolygon(locationI2, locationF2)
    
    Poly3 = p3.getScaledPolygon(locationI2, locationF2)
    
    # x3, y3 = Poly1.exterior.xy
    
    x5, y5 = Poly3.exterior.xy
    
    
    # ax.fill(x3, y3, alpha=0.5, fc='blue', label='P1 1')
    
    ax2.fill(x5, y5, alpha=0.5, fc='red', label='P2 2')

    plt.show()



