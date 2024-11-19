import numpy as np
import statistics as st
import string
from datetime import datetime
import os
import re
import math
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

"""
Changes to code (10/5/22):
-Added retraction every time a '2' move occurs. A '2' move signifies a new cell
-Removed slight retraction every '0' move. A '0' move signifies a new shell.
The retraction was added to prevent buildup of material at the seam, but did not
help. Instead, it created a larger mound of material.
-Added raise command during '2' move. This prevents dragging across other
complete cells
-Use G0 movement for non printing moves
"""




class Conversion:

	def __init__(self, inputFileR1, inputFileR2, updatedFileR1, updatedFileR2):
		self.inputFileR1 = inputFileR1
		self.inputFileR2 = inputFileR2
		self.updatedFileR1 = updatedFileR1
		self.updatedFileR2 = updatedFileR2

	def convertR2(self):
		#filename = 'robot2_quad_updated' + '.txt'

		filename = self.updatedFileR2
		with open(self.inputFileR2, "r", encoding="utf8") as myfile:
			with open(filename, "w", encoding='utf8') as replaced:

				for line in myfile.readlines():
					if 'Layer' in line:
						newline = line

					elif 'Interfacing' in line or "Non-interfacing" in line:
						newline = line

					else:
						data = line.split()
						x = float(data[0])
						y = float(data[1])
						# t = int(data[3])
                        #Printer Set 1 ()
                        
						x_new = 300 - x + 48.5 #300 - x - .5
						y_new = 300 - y + 200 + 3# 300 - y + 150 - .5
                        
                        
                    

						newline = str(x_new) + ' ' + str(y_new) + ' ' + data[2] + ' '+data[3] + '\n'
						#print("newlie2", newline)

					replaced.write(newline)

	def convertR1(self):
		# filename = 'robot1_quad_updated' + '.txt'

		filename2 = self.updatedFileR1
		with open(self.inputFileR1, "r", encoding="utf8") as myfile:
			with open(filename2, "w", encoding='utf8') as replaced:

				for line in myfile.readlines():
					if 'Layer' in line:
						newline = line

					elif 'Interfacing' in line or "Non-interfacing" in line:
						newline = line

					else:
						data = line.split()
						x = float(data[0])
						y = float(data[1])
						x_new = x - 100 + 49  # x - 0
						y_new = y - 0 + 100 - 2.5  # y - 0 + 150

						newline = str(x_new) + ' ' + str(y_new) + ' ' + data[2] + ' ' +data[3] + '\n'
						#print("newline1", newline)

					replaced.write(newline)



class ManualGcode:

	def __init__(self, initial_gcode_robot1, initial_gcode_robot2, final_gcode_robot, diameter, layerHeight, linewidth):
		self.initial_gcode_robot1 = initial_gcode_robot1
		self.initial_gcode_robot2 = initial_gcode_robot2
		self.final_gcode_robot = final_gcode_robot
		self.diameter = diameter
		self.layerHeight = layerHeight
		self.linewidth = linewidth

	def extrusionCalculator(self, locations):
		diameter = self.diameter
		layerHeight = self.layerHeight + 0.10
		linewidth = self.linewidth

		# locations used for calculation of the volume of extrusion
		x1 = locations[0][0]
		x2 = locations[1][0]
		y1 = locations[0][1]
		y2 = locations[1][1]
		length = math.hypot(x2-x1, y2-y1)

		#calcualate the area and then the volume of the cylinder
		areaRoad = (linewidth - layerHeight)*layerHeight+math.pi*((layerHeight/2)**2)
		exrudedAmount = areaRoad*length*4/(math.pi*diameter**2)

		return exrudedAmount

	def generateGcodeR1(self, layerHeight):
		# d = 2.85
	 #    layer_height = 0.45
	 #    linewidth = 0.65

		filename = 'AMBOT1_' + \
			str(datetime.now().strftime('%Y_%m_%d_%H_%M')) + '.gcode'
		z = layerHeight #+ 16.45
		goToStart = "G0 X300 Y20 Z50 \n"
		# startup routine for the printers
		initial_gcode = self.initial_gcode_robot1
		with open("robot1.txt", "r") as myfile:
			with open(filename, "w") as replaced:
				# set up initial parameters
				i = 0
				x_prev = 0
				y_prev = 0
				t_prev = 0
				lineprev = ""
				replaced.write(initial_gcode)

				for line in myfile.readlines():
					if 'Layer' in line:
						z += layerHeight
						lineprev = line
						# replaced.write(goToStart)
						# new_code = 'M291 P"Wait " S3 \n G1 F200 E3 ;extrude 3mm of feed stock \n M400 \n'
# 						newline = "M25\n" + \
# 						"M104 S240\n"
# 						replaced.write(newline)
						# replaced.write(new_code)
					elif 'Interfacing' in line:
						if 'Layer' in lineprev:
							newline = "M117 Interfacing\n" + \
                            "M25\n" + \
                            "M104 S240\n"
							replaced.write(newline)
						else:
							newline = "M117 Interfacing\n"
							replaced.write(newline)
					elif "Non-interfacing" in line:
						if 'Layer' in lineprev:
							newline = "M117 Non-Interfacing\n" + \
                            "M25\n" + \
                            "M104 S240\n"
							replaced.write(newline)
						else:
							newline = "M117 Non-Interfacing\n"
							replaced.write(newline)

					else:
						# splits the line and assings x, y and t values
						data = line.split()
						x = float(data[0])
						y = float(data[1])
						#Z = float(data[2])
						t = int(data[3])

						if i == 0:
							newline = "G1 X" + str(x) + ' Y' + str(y) + '\n'
						else:
							points = [(x_prev, y_prev), (x, y)]
							if t_prev == 1:
								eValue = self.extrusionCalculator(points)
								newline = "G1 X" + str(x) + ' Y' + str(y) + ' Z' + str(z) + ' E' + str(eValue) + '\n'
							elif t_prev == 2:                    
								newline = "G92 E0\n" + \
                                    "G1 E-3.0000 F3000\n" + \
                                    "G0 Z" + str(z+5) + \
                                    "G0 X" + str(x) + ' Y' + str(y) + ' Z' + str(z+5) + '\n' + \
                                    "G0 Z" + str(z) + \
                                    "G1 E3.0000 F3000\n" + \
                                    "G92 E0\n"
							else:
								newline = "G0 X" + str(x) + ' Y' + str(y) + ' Z' + str(z) + '\n'
                                                
						replaced.write(newline)
						x_prev = float(x)
						y_prev = float(y)
						t_prev = t
						i = i + 1
						lineprev = line
				replaced.write(final_gcode)


	def generateGcodeR2(self, layerHeight):

		filename = 'AMBOT2_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M')) + '.gcode'

		initial_gcode = self.initial_gcode_robot2
		z = layerHeight #+ 19.8
		goToStart = "G0 X300 Y20 Z10 \n"
		with open("robot2.txt", "r") as myfile:
			with open(filename, "w") as replaced:
				i = 0
				x_prev = 0
				y_prev = 0
				t_prev = 0
				lineprev = ""
				replaced.write(initial_gcode)

				for line in myfile.readlines():
					if 'Layer' in line:
						z += layerHeight
						lineprev = line
						# replaced.write(goToStart)
						# new_code = 'M291 P"Wait " S3 \n G1 F200 E3 ;extrude 3mm of feed stock \n M400 \n'
# 						newline = "M25\n" + \
# 						"M104 S240\n"
# 						replaced.write(newline)
						# replaced.write(new_code)
					elif 'Interfacing' in line:
						if 'Layer' in lineprev:
							newline = "M117 Interfacing\n" + \
                            "M25\n" + \
                            "M104 S240\n"
							replaced.write(newline)
						else:
							newline = "M117 Interfacing\n"
							replaced.write(newline)
					elif "Non-interfacing" in line:
						if 'Layer' in lineprev:
							newline = "M117 Non-Interfacing\n" + \
                            "M25\n" + \
                            "M104 S240\n"
							replaced.write(newline)
						else:
							newline = "M117 Non-Interfacing\n"
							replaced.write(newline)
                        
					else:
						data = line.split()
						x = float(data[0])
						y = float(data[1])
						#Z = float(data[2])
						t = int(data[3])

						if i == 0:
							newline = "G1 X" + str(x) + ' Y' + str(y) + '\n'
						else:
							points = [(x_prev, y_prev), (x, y)]
							if t_prev == 1:
								eValue = self.extrusionCalculator(points)
								newline = "G1 X" + str(x) + ' Y' + str(y) + ' Z' + str(z) + ' E' + str(eValue) + '\n'
							elif t_prev == 2:                    
								newline = "G92 E0\n" + \
                                    "G1 E-3.0000 F3000\n" + \
                                    "G0 Z" + str(z+5) + \
                                    "G0 X" + str(x) + ' Y' + str(y) + ' Z' + str(z+5) + '\n' + \
                                    "G0 Z" + str(z) + \
                                    "G1 E3.0000 F3000\n" + \
                                    "G92 E0\n"
							else:
# 								newline = "G0 X" + str(x) + ' Y' + str(y) + ' Z' + str(z) + '\n'
								newline = ""

						replaced.write(newline)
						x_prev = float(x)
						y_prev = float(y)
						t_prev = t
						i = i + 1
						lineprev = line
				replaced.write(final_gcode)



if __name__ == '__main__':
	initial_gcode_robot_1 = '''M117
    M104 S240
	M105
	M109 S240
	M82 ;absolute extrusion mode
	G1 Z15.0 F6000 ;Move the platform down 15mm
	;Prime the extruder
	G92 E0
	G1 F200 E3
	G92 E0
	M83 ;relative extrusion mode
	G1 F1200 E-5.6
	;LAYER_COUNT:80
	;LAYER:0
	M400
	M107
	M204 S5000
	G1 F600 Z1.45
	G0 F900 X215.005 Y128.49 Z1.45
	M204 S100
	;TYPE:WALL-OUTER
	G1 F600 Z0.45
	G1 F1200 E5.61568\n'''

	initial_gcode_robot_2 = '''M104 S240
	M105
	M109 S240
	M82 ;absolute extrusion mode
	G1 Z15.0 F6000 ;Move the platform down 15mm
	;Prime the extruder
	G92 E0
	G1 F200 E3
	G92 E0
	M83 ;relative extrusion mode
	G1 F1200 E-5.6
	;LAYER_COUNT:80
	;LAYER:0
	M400
	M107
	M204 S5000
	G1 F600 Z1.45
	G0 F900 X215.005 Y128.49 Z1.45
	M204 S100
	;TYPE:WALL-OUTER
	G1 F600 Z0.45
	G1 F1200 E5.61568\n'''

	final_gcode = '''G1 F1200 E-5.6
	M204 S4000
	M82 ;absolute extrusion mode
	M104 S0
	M140 S0
	;Retract the filament
	G92 E1
	G1 E-1 F300
	G28 X0 Y0
	M84
	M82 ;absolute extrusion mode
	M104 S0\n'''


	# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
	inputfileR1 = askopenfilename() # show an "Open" dialog box and return the path to the selected file
	inputfileR2 = askopenfilename()


	# inputfileR1 = 'robot1_quad.txt'
	# inputfileR2 = 'robot2_quad.txt'
	filename1 = './robot1.txt'
	filename2 = './robot2.txt'
	convertfile = Conversion(inputfileR1, inputfileR2, filename1, filename2)
	convertfile.convertR1()
	convertfile.convertR2()

	# parameters associated with the calculation of volume of extrusion
	diameter = 1.75
	layerHeight = 0.45 # change the height based on the file provided
	linewidth = 0.42 #adjust to change extrusion rate
	createGcode = ManualGcode(initial_gcode_robot_1, initial_gcode_robot_2, final_gcode,
							diameter, layerHeight, linewidth)

	createGcode.generateGcodeR1(layerHeight)
	createGcode.generateGcodeR2(layerHeight)
