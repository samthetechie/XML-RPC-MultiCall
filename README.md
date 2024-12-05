# **XML-RPC-MultiCall Stress Testing & Brute Force Suite** 🚀

## **Overview**
This repository contains tools developed during a HackTheBox CTF to improve stress-testing and brute-forcing XML-RPC endpoints. The tools include:

1. **Stress Testing Suite**: This tool evaluates and analyses server rate-limiting, request handling, and performance using ApacheBench and parallel requests. **It should be run first**, as it helps determine the optimal parameters for the MultiCall Brute Force Tool.
   
2. **MultiCall Brute Force Tool**: This tool uses XML-RPC’s `MultiCall` functionality to perform multiple authentication attempts in a single request, optimizing the speed of brute-force attacks. The parameters used in this tool (such as batch size, delay, and retries) are dynamically determined by the results from the Stress Testing Suite.

Both tools are designed to maximise efficiency while respecting server constraints, making the brute-forcing process both faster and more resilient to rate limits.

---

## **Workflow**
1. **Run the Stress Testing Suite First**: 
   - The Stress Testing Suite analyses the server’s response under load, measures requests per second (RPS), and examines rate-limiting behavior. This helps determine the optimal values for the brute-force attack parameters such as batch size and delay.
   
2. **Run the MultiCall Brute Force Tool**: 
   - After running the stress tests and obtaining key parameters (such as optimal delay and batch size), use them to configure and run the MultiCall Brute Force Tool. This tool will apply the optimized settings to perform the brute-force attack more efficiently.


## **Features**
### **Stress Testing Suite**
- **Curl Info Analysis**: Extracts headers to analyze rate-limiting behavior, such as `Retry-After` and rate limit values.
- **ApacheBench Stress Testing**: Measures server throughput (requests per second) and time per request to understand server performance under load.
- **Parallel Curl Bursts**: Simulates burst traffic to test the server's capacity to handle multiple concurrent requests.
- **Dynamic Parameter Optimization**: Based on test results, the suite suggests values for batch size, delay, and concurrency, which will be used in the next step.

### **MultiCall Brute Force Tool**
- **MultiCall Optimization**: Sends multiple login attempts in one XML-RPC request, speeding up brute-force attempts.
- **Dynamic Batch Adjustment**: The batch size is automatically adjusted based on server performance data gathered from the Stress Testing Suite.
- **Rate Limiting Awareness**: Adaptive delays are applied based on server responses, ensuring that the brute-force tool doesn't trigger rate-limiting.
- **Error Handling**: Gracefully handles connection issues, server faults, and unexpected errors.

---

## **Usage**
#### Prerequisites
- Python 3.x
- Required tools: `curl`, `ApacheBench (ab)`
- `rockyou.txt` or another password wordlist (default e.g. on Kali Linux: `/usr/share/wordlists/rockyou.txt`)
- XML-RPC server endpoint. e.g. on Wordpress

### Setup
#### Clone the repository:
```bash
git clone https://github.com/samthetechie/xmlrpc-multicall-bruteforce.git
cd xmlrpc-multicall-bruteforce
```

## **Running the Tools**


#### **Step 1: Run the Stress Testing Suite**
Run the stress test suite to determine optimal parameters for the brute-force tool:

#### Run the tool using:
```bash
python3 stress_test_suite.py
```

#### Customise:
- target_url: URL for the target server.

The Stress Testing Suite will provide feedback on the server's performance and suggest settings for the next step.

#### **Step 2: Run the MultiCall Brute Force Tool**

Once you have the optimal parameters from the Stress Testing Suite, you can run the MultiCall Brute Force tool with the Customised settings:
```bash
python3 multicall_bruteforce.py
```
#### Customise:
- Use the parameters recommended by the Stress Testing Suite, such as batch_size, delay, and max_retries.
- target_url: XML-RPC server endpoint
- username: Target username.
- password_file: Path to your password wordlist

    