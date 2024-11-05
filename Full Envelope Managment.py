# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 15:14:44 2024

@author: Siddh
"""
# import TestCode
import math
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

#Polygon Plotting
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import scale

class printer:
    def __init__ (self, OriginLocation, PrinterOffset, ax, PrinterDimensions = 300, PrinterName = "p", armOneLength = 217, armTwoLength = 204):
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
        
        self.PrinterTransformation =  transforms.Affine2D().rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2]) + ax.transData
        self.PrinterCoordTranslation = transforms.Affine2D().translate(self.OriginLocation[0], self.OriginLocation[1]).rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2])+ ax.transData
        
        self.armOneLength = armOneLength
        self.armTwoLength = armTwoLength
        
        self.scaleFactor = 5
        
        #Set up the graph of the base
        self.baseLocation = plt.plot(self.getPrinterPoint()[0], self.getPrinterPoint()[1], self.Name, transform = self.PrinterTransformation)
        ax.add_patch(self.getBuildSurfaceRectangle())
        
        
        
    def getBuildSurfaceRectangle(self):
        """Returns the print envelope of the printer as a recangle object"""
        return plt.Rectangle((self.OriginLocation[0],self.OriginLocation[1]),
                              self.PrinterDimensions, self.PrinterDimensions , 
                              linewidth=2, edgecolor='r', facecolor='none', transform=self.PrinterTransformation)
    
    def getPrinterPoint(self):
        """Returns a tuple of the printer's base coordinates"""
        return (self.OriginLocation[0] + self.PrinterOffset[0], self.OriginLocation[1] + self.PrinterOffset[1])
    
    def getEndPosition(self):
        return(0,0,0)
    
    
    def plotPrinterPoint(self, xyz):
        """Takes a tuple (x,y,z)"""
        plt.plot(xyz[0], xyz[1], self.Name, transform = self.PrinterCoordTranslation)
    
    def getJointLocation(self, xyz, plot = False):
        """Takes a tuple (x,y,z)"""
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
    
    def getPolygonCoords(self, xyzI, xyzF):
        
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
        transformed_points = np.insert(transformed_points, 5, BasePos, axis = 0)
        
        rot = transforms.Affine2D().rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2])
        
        rotated_points = rot.transform(transformed_points)
        
        print(rotated_points)
        print(polyTup)
        return rotated_points
        # return polyTup
    
    
    # def returnTransformation(self):
    #     return self.PrinterCoordTranslation
    
    def getScaledPolygon(self, xyzI, xyzF):
        
        p = Polygon(self.getPolygonCoords(xyzI, xyzF))
        
        # s_fact = 1 + self.scaleFactor
        # base = (int(self.baseLocation[0].get_xdata()[0]), int(self.baseLocation[0].get_ydata()[0]))
        # scaled = scale(p, xfact = s_fact, yfact = s_fact, origin = base)
        
        scaled = p.buffer(self.scaleFactor)
        
        return scaled
    
    def getPolygon(self, xyzI, xyzF):
        
        p = Polygon(self.getPolygonCoords(xyzI, xyzF))
        
        return p
    
        
        
        
        
# class envelope:
#     def __init__(self, printers):
#         self.fig, self.ax = plt.subplots()
        
#         for p in printers:
#             self.printers.append(p)
            
#             rect = patches.Rectangle(p.getOrigin(), p.getWidth(), p.getHeight(), linewidth=2, edgecolor='r', facecolor='none')
#             self.ax.add_patch(rect)
#             #self.
#         plt.show()

if __name__ == "__main__":
    # e = envelope([])
    
    fig, ax = plt.subplots()
    
    ax.set_xlim(-500, 500)
    ax.set_ylim(-500, 500)
    
    p = printer((50,50,0), (150, -35), ax)
    
    # print(p.getLocations((0,0,0)))
    
    locationI = (0,300,0)
    locationF = (300,300,0)
    
    p.plotPrinterPoint(locationI)
    p.getJointLocation(locationI, True)
    
    p.plotPrinterPoint(locationF)
    p.getJointLocation(locationF, True)
    
    polygon1 = p.getPolygon(locationI, locationF)
    
    polygon2 = p.getScaledPolygon(locationI, locationF)
    
    
    
    
    
    x1, y1 = polygon1.exterior.xy
    
    x2, y2 = polygon2.exterior.xy
    
    
    # transform = p.returnTransformation()
    
    # tfC1 = transform.transform(list(zip(x1, y1)))
    # transformed_polygon = Polygon(tfC1)
    
    # ax.plot(*transformed_polygon.exterior.xy, color='red', label='Transformed')

    
    
    
    ax.fill(x1, y1, alpha=0.5, fc='blue', label='Polygon 1')
    
    ax.fill(x2, y2, alpha=0.5, fc='red', label='Polygon 2')
    



    plt.show()



