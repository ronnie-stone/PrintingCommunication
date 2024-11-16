import requests # sending HTTP requests.
import time # checking latency values.
import matplotlib.pyplot as plt # plotting.


def simple_latency_test(printer_ip, delay_value, num_requests):

    latencies = []

    total_start_time = time.time()

    for i in range(num_requests):
        time.sleep(delay_value)
        start_time = time.time()
        try:
            r1 = request_status(printer_ip)
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

        print()
        print(f"Total Running Time: {total_time:.4f} seconds")
        print(f"Max Latency: {max_latency:.4f} seconds")
        print(f"Min Latency: {min_latency:.4f} seconds")
        print(f"Average Latency: {avg_latency:.4f} seconds")

    else:
        print("No latencies available!")

    return latencies

def request_status(ip):

    base_request = ("http://{0}:{1}/rr_status?type=0").format(ip,"")
    return requests.get(base_request).json()

if __name__ == "__main__":

    # Choose printer IP for latency test. Machine must be connected to AMBOTS network. 
    printer_ip = "192.168.0.14"

    # Choose delay value. This is the minimum time taken between consecutive requests. 
    delay_value = 0.05

    # Choose the number of requests to make the test statistically significant. 
    num_requests = 1000

    latencies = simple_latency_test(printer_ip, delay_value, num_requests)

    plt.plot(list(range(num_requests)), latencies)
    plt.title("Latency Plot")
    plt.xlabel("Request Number")
    plt.ylabel("Latency (s)")
    plt.show()

