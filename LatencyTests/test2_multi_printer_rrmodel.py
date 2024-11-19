import asyncio
import aiohttp  # For asynchronous HTTP requests
import time
import matplotlib.pyplot as plt


async def fetch_status(session, printer_ip, timeout):
    """Asynchronously fetch printer status and measure latency."""
    url = f"http://{printer_ip}/rr_model?key=move.axes[].machinePosition"
    start_time = time.time()
    try:
        async with session.get(url, timeout=timeout) as response:
            await response.json()  # Parse the JSON response
            latency = time.time() - start_time
            return printer_ip, latency
    except Exception as e:
        print(f"{printer_ip} - Error: {e}")
        return printer_ip, 2 * timeout  # Assign a high latency for failed requests


async def test_printer_latencies(printer_ips, timeout, num_requests):
    """Test latencies for a list of printer IPs asynchronously, tracking batch completion time."""
    latencies = {ip: [] for ip in printer_ips}
    batch_latencies = []  # Track time taken to complete each batch

    total_start_time = time.time()

    async with aiohttp.ClientSession() as session:
        for i in range(num_requests):
            start_time = time.time()  # Start of batch
            tasks = [fetch_status(session, ip, timeout) for ip in printer_ips]
            results = await asyncio.gather(*tasks)  # Wait for all printers in the batch
            end_time = time.time()  # End of batch

            # Calculate batch latency
            batch_latency = end_time - start_time
            batch_latencies.append(batch_latency)

            # Collect latencies for each printer
            for printer_ip, latency in results:
                latencies[printer_ip].append(latency)
                print(f"Request {i} - {printer_ip}: {latency:.4f} seconds")

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


if __name__ == "__main__":
    # List of printer IPs
    printer_ips = ["192.168.0.14", "192.168.0.15", "192.168.0.16"]

    # Timeout and number of requests
    timeout = 0.1
    num_requests = 100

    # Run the latency test
    latencies, batch_latencies = asyncio.run(test_printer_latencies(printer_ips, timeout, num_requests))

    # Plot the results
    plot_latencies(latencies, batch_latencies, num_requests)