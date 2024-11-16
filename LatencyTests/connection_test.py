import requests # allows you to send HTTPS requests
import json
import time
import asyncio 


gcode_list = {"M291": 'M291 P"Waiting for permission to continue" S3', # pauses printer to wait to be allowed to start again
              "M292": 'M292',       # Unpauses M291 command
              "M23": 'M23',         # Selects sd card file for printing
              "M24": 'M24',         # Starts or Resumes Print from an sd card
              "M25": 'M25',         # Pause a print from an sd card - runs pause.g macro.
              "M226": 'M226',       # Never Used
              "M104": 'M104 S240',  # Sets the extruder temperature to 240C
              "M408": 'M408 S0',    # Returns the status of the printer in json style. More info: https://reprap.org/wiki/G-code#M408:_Report_JSON-style_response
              "M409": 'M409 K"move.axes[].machinePosition"'}

ip4 = "192.168.0.14"
ip5 = "192.168.0.15"

def issue_gcode(ip, com, filename=""):

    base_request = ("http://{0}:{1}/rr_gcode?gcode=" + gcode_list[com] + filename).format(ip,"")
    r = requests.get(base_request).json()
    return r

def request_joblist(ip):

    base_request = ("http://{0}:{1}/rr_filelist?dir=gcodes").format(ip,"")
    return requests.get(base_request).json()

def request_status(ip):

    base_request = ("http://{0}:{1}/rr_status?type=0").format(ip,"")
    return requests.get(base_request).json()

if __name__ == "__main__":

    ip_P1 = ip4
    ip_P2 = ip5

    latencies = []

    num_requests = 1000

    total_start_time = time.time()

    for i in range(num_requests):
        time.sleep(0.01)
        start_time = time.time()
        try:
            r1 = request_status(ip_P1)
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            print(i)
        except:
            print("Could not get request!")
            break

    total_end_time = time.time()
    total_time = total_end_time - total_start_time


    if latencies:
        max_latency = max(latencies)
        min_latency = min(latencies)
        avg_latency = sum(latencies) / len(latencies)

        # Printing Results
        print()
        print(f"Total Running Time: {total_time:.4f} seconds")
        print(f"Max Latency: {max_latency:.4f} seconds")
        print(f"Min Latency: {min_latency:.4f} seconds")
        print(f"Average Latency: {avg_latency:.4f} seconds")

    else:
        print("No latencies available!")

    # while True:
    #     r = request_status(ip_P1)
    #     print(r['coords']['machine'])
    #     time.sleep(0.1)

