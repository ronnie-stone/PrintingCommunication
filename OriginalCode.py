import requests # allows you to send HTTPS requests
import json
import time

gcode_list = {"M291": 'M291 P"Waiting for permission to continue" S3', # pauses printer to wait to be allowed to start again
              "M292": 'M292',       # Unpauses M291 command
              "M23": 'M23',         # Selects sd card file for printing
              "M24": 'M24',         # Starts or Resumes Print from an sd card
              "M25": 'M25',         # Pause a print from an sd card - runs pause.g macro.
              "M226": 'M226',       # Never Used
              "M104": 'M104 S240',  # Sets the extruder temperature to 240C
              "M408": 'M408 S0'}    # Returns the status of the printer in json style. More info: https://reprap.org/wiki/G-code#M408:_Report_JSON-style_response

ip7 = "192.168.0.17"
ip5 = "192.168.0.15"

def issue_gcode(ip, com, filename=""):

	base_request = ("http://{0}:{1}/rr_gcode?gcode=" + gcode_list[com] + filename).format(ip,"")
	r = requests.get(base_request)
	return r

def request_joblist(ip):

	base_request = ("http://{0}:{1}/rr_filelist?dir=gcodes").format(ip,"")
	return requests.get(base_request).json()

def request_status(ip):

	base_request = ("http://{0}:{1}/rr_status?type=0").format(ip,"")
	return requests.get(base_request).json()

if __name__ == "__main__":

	ip_P1 = ip5
	ip_P2 = ip7
	file_P1 = "AMBOT1_2022_10_13_16_08.gcode"
	file_P2 = "AMBOT2_2022_10_13_16_08.gcode"

	issue_gcode(ip_P1, "M23", file_P1)
	issue_gcode(ip_P2, "M23", file_P2)

	issue_gcode(ip_P1, "M24")
	issue_gcode(ip_P2, "M24")

	time.sleep(1)

	interfacing_P1 = True
	interfacing_P2 = True

	status_P1 = request_status(ip_P1)
	status_P2 = request_status(ip_P2)

	while status_P1["status"] != "I" and status_P2["status"] != "I":

		if interfacing_P1 and interfacing_P2:

			issue_gcode(ip_P2, "M25")

		time.sleep(0.5)

		status_P1 = request_status(ip_P1)
		status_P2 = request_status(ip_P2)

		if status_P2["status"] == "S" and not interfacing_P1:

			issue_gcode(ip_P2, "M24")

		time.sleep(0.5)

		status_P1 = request_status(ip_P1)
		status_P2 = request_status(ip_P2)

		try: 

			message = status_P1["output"]["message"]

			if message == "Interfacing": interfacing_P1 = True

			else: interfacing_P1 = False

		except: pass

		try: 

			message = status_P2["output"]["message"]

			if message == "Interfacing": interfacing_P2 = True

			else: interfacing_P2 = False

		except: pass

		status_P1 = request_status(ip_P1)
		status_P2 = request_status(ip_P2)

		time.sleep(0.5)

		pos_P1 = status_P1["coords"]["xyz"]
		pos_P2 = status_P2["coords"]["xyz"]

		temp_P1 = status_P1["temps"]["current"]
		temp_P2 = status_P2["temps"]["current"]

		print("Printer 1: ", status_P1, pos_P1, "Temperature: ", temp_P1, "Printer 2 :", status_P2, pos_P2, "Temperature: ", temp_P2)