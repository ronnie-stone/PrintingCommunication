# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 15:14:44 2024

@author: Siddh
"""
import TestCode
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import matplotlib.patches as patches

class printer:
    def __init__ (self, OriginLocation, PrinterOffset, PrinterDimensions = 300, PrinterName = "p", armOneLength = 217, armTwoLength = 204):
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
        self.PrinterOffset = PrinterOffset
        self.PrinterDimensions = PrinterDimensions
        
        self.armOneLength = armOneLength
        self.armTwoLength = armTwoLength
        
        
        ##Coordinate Management
        # theta (0,0) means the printer head is located at (300,0)
        self.arm1angle = 0 
        self.arm2angle = 0
        
        
        
    def getBuildSurfaceRectangle(self, fig, ax):
        """Returns the print envelope of the printer as a recangle object"""
        t = transforms.Affine2D().rotate_deg_around(self.OriginLocation[0], self.OriginLocation[1], self.OriginLocation[2]) + ax.transData
        return plt.Rectangle((self.OriginLocation[0],self.OriginLocation[1]),
                              self.PrinterDimensions, self.PrinterDimensions , 
                              linewidth=2, edgecolor='r', facecolor='none', transform=t)
    
    def getPrinterPoint(self):
        """Returns a tuple of the printer's base coordinates"""
        return (self.OriginLocation[0] + self.PrinterOffset[0], self.OriginLocation[1] + self.PrinterOffset[1])
    
    def plot(self, fig, ax):
        ax.add_patch(self.getBuildSurfaceRectangle(fig,ax))
        plt.plot(self.getPrinterPoint()[0], self.getPrinterPoint()[1], self.Name) 
        
        
        
        
        
        
class envelope:
    def __init__(self, printers):
        self.fig, self.ax = plt.subplots()
        
        for p in printers:
            self.printers.append(p)
            
            rect = patches.Rectangle(p.getOrigin(), p.getWidth(), p.getHeight(), linewidth=2, edgecolor='r', facecolor='none')
            self.ax.add_patch(rect)
            #self.
        plt.show()

if __name__ == "__main__":
    e = envelope([])
    
    fig, ax = plt.subplots()
    
    ax.set_xlim(-50, 500)
    ax.set_ylim(-50, 500)
    
    p = printer((0,0,0), (150, -30))
    p.plot(fig,ax)
    
    



    plt.show()



