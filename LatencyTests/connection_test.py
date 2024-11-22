import asyncio
import aiohttp  # For asynchronous HTTP requests
import time
import matplotlib.pyplot as plt
from datetime import datetime


def plot_latencies(latencies, batch_latencies, num_requests):
    """Plot latencies for all printers and batch latencies."""
    for ip, lats in latencies.items():
        plt.plot(range(num_requests), lats, label=f"Printer {ip}")

    plt.plot(range(num_requests), batch_latencies, label="Batch Latency", linestyle="--", linewidth=2, color="black")
    plt.title("Latency Plot")
    plt.xlabel("Request Number")
    plt.ylabel("Latency (s)")
    plt.legend()
    plt.show()


async def fetch_status(session, printer_ip, timeout):

    url = f"http://{printer_ip}/rr_status?type=0"
    start_time = time.time()

    try:
        async with session.get(url, timeout=timeout) as response:
            data = await response.json()  
            latency = time.time() - start_time
            return printer_ip, latency, data

    except Exception as e:
        print(f"{printer_ip} - Error: {e}")
        return printer_ip, 2 * timeout, {"status": "", "coords": {"machine": ""}, "speeds": {"requested": ""}}  # Failure Line

async def test_printing_process(printer_ips, timeout, gcode_files):
    """Test latencies for a list of printer IPs asynchronously, tracking batch completion time."""
    latencies = {ip: [] for ip in printer_ips}
    batch_latencies = []  # Track time taken to complete each batch

    total_start_time = time.time()

    async with aiohttp.ClientSession() as session:

        for i in range(num_requests):

            start_time = time.time()

            tasks = [fetch_status(session, ip, timeout) for ip in printer_ips]
            results = await asyncio.gather(*tasks)  # Wait for all printers in the batch
            end_time = time.time()  # End of batch

            # Calculate batch latency
            batch_latency = end_time - start_time
            batch_latencies.append(batch_latency)

            # Collect latencies for each printer
            for printer_ip, latency, response in results:
                latencies[printer_ip].append(latency)
                print(f"Request {i} - {printer_ip}: {latency:.4f} seconds")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                logging_file.write(f"Timestamp: {timestamp}, Printer: {printer_ip}, Position: {response['coords']['machine']}, Feedrate: {response['speeds']['requested']}, Status: {response['status']}\n")

    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    print("\nSummary:")
    for ip, lats in latencies.items():
        if lats:
            print(f"Printer {ip} - Max: {max(lats):.4f}s, Min: {min(lats):.4f}s, Avg: {sum(lats)/len(lats):.4f}s")
        else:
            print(f"Printer {ip} - No data available!")

    print(f"\nTotal Running Time: {total_time:.4f} seconds")
    print(f"Minimum Batch Latency: {min(batch_latencies):.4f} seconds")
    print(f"Maximum Batch Latency: {max(batch_latencies):.4f} seconds")
    print(f"Average Batch Latency: {sum(batch_latencies)/len(batch_latencies):.4f} seconds")
    
    return latencies, batch_latencies
    


async def test_printer_latencies(printer_ips, timeout, num_requests):
    """Test latencies for a list of printer IPs asynchronously, tracking batch completion time."""
    latencies = {ip: [] for ip in printer_ips}
    batch_latencies = []  # Track time taken to complete each batch

    total_start_time = time.time()

    async with aiohttp.ClientSession() as session:

        for i in range(num_requests):

            start_time = time.time()

            tasks = [fetch_status(session, ip, timeout) for ip in printer_ips]
            results = await asyncio.gather(*tasks)  # Wait for all printers in the batch
            end_time = time.time()  # End of batch

            # Calculate batch latency
            batch_latency = end_time - start_time
            batch_latencies.append(batch_latency)

            # Collect latencies for each printer
            for printer_ip, latency, response in results:
                latencies[printer_ip].append(latency)
                print(f"Request {i} - {printer_ip}: {latency:.4f} seconds")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                logging_file.write(f"Timestamp: {timestamp}, Printer: {printer_ip}, Position: {response['coords']['machine']}, Feedrate: {response['speeds']['requested']}, Status: {response['status']}\n")

    total_end_time = time.time()
    total_time = total_end_time - total_start_time

    print("\nSummary:")
    for ip, lats in latencies.items():
        if lats:
            print(f"Printer {ip} - Max: {max(lats):.4f}s, Min: {min(lats):.4f}s, Avg: {sum(lats)/len(lats):.4f}s")
        else:
            print(f"Printer {ip} - No data available!")

    print(f"\nTotal Running Time: {total_time:.4f} seconds")
    print(f"Minimum Batch Latency: {min(batch_latencies):.4f} seconds")
    print(f"Maximum Batch Latency: {max(batch_latencies):.4f} seconds")
    print(f"Average Batch Latency: {sum(batch_latencies)/len(batch_latencies):.4f} seconds")
    
    return latencies, batch_latencies

async def main():

    # Define global variables of interest:

    global logging_file
    global printer_status
    global printer_positions

    # Define and open logging file:

    logging_file = open("logging_file.txt", "w")

    # List of printer IPs:

    printer_ips = ["192.168.0.14", "192.168.0.15", "192.168.0.16"]

    # Parameters:

    printer_status = [None]*len(printer_ips)
    printer_positions = [None]*len(printer_ips)
    timeout = 0.2
    num_requests = 1000

    # Get initial values:

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, ip, timeout) for ip in printer_ips]
        results = await asyncio.gather(*tasks) 

        i = 0
        for printer_ip, latency, response in results:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            printer_positions[i] = response['coords']['machine']
            printer_status[i] = response['status']
            logging_file.write(f"Timestamp: {timestamp}, Printer: {printer_ip}, Position: {response['coords']['machine']}, Feedrate: {response['speeds']['requested']}, Status: {response['status']}\n")
            i += 1

        # Run the latency test:

    latencies, batch_latencies = await test_printer_latencies(printer_ips, timeout, num_requests)

    # Plot the results

    # plot_latencies(latencies, batch_latencies, num_requests)

    logging_file.close()

if __name__ == "__main__":
    asyncio.run(main())