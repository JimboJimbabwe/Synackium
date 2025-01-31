import json
import subprocess
import time
import re

def reverse_ip_to_arpa(ip):
    """Convert IP to reverse DNS format (e.g., 192.0.5.5 -> 5.5.0.192.in-addr.arpa.)"""
    octets = ip.split('.')
    return f"{'.'.join(octets[::-1])}.in-addr.arpa."

def extract_question_section(dig_output):
    """Extract the reversed IP from QUESTION SECTION"""
    lines = dig_output.split('\n')
    for i, line in enumerate(lines):
        if ';; QUESTION SECTION:' in line and i + 1 < len(lines):
            question_line = lines[i + 1].strip()
            # Extract the reversed IP part (remove leading semicolon if present)
            reversed_ip = question_line.lstrip(';').split()[0]
            return reversed_ip
    return None

def perform_dig_lookup(ip):
    """Perform dig lookup and verify reversed IP"""
    result = {
        "original_ip": ip,
        "expected_reverse": reverse_ip_to_arpa(ip),
        "found_reverse": None,
        "matches": False,
        "raw_output": None,
        "error": None
    }
    
    try:
        # Run dig command
        cmd = ['dig', '-x', ip]
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            result["error"] = f"dig command failed: {process.stderr}"
            return result
        
        # Store raw output
        result["raw_output"] = process.stdout
        
        # Extract reversed IP from QUESTION SECTION
        found_reverse = extract_question_section(process.stdout)
        if found_reverse:
            result["found_reverse"] = found_reverse
            result["matches"] = (found_reverse == result["expected_reverse"])
        
    except Exception as e:
        result["error"] = f"Error: {str(e)}"
    
    return result

def process_ips(input_file, json_file, output_file):
    """Process list of IPs and save results"""
    # Read IPs
    with open(input_file, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    print(f"Processing {len(ips)} IPs...")
    
    # Process each IP
    results = {}
    for ip in ips:
        print(f"Looking up {ip}...")
        results[ip] = perform_dig_lookup(ip)
        time.sleep(10)  # Wait between requests
    
    # Save detailed results to JSON
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=4)
    
    # Create human-readable report
    with open(output_file, 'w') as f:
        f.write("Dig Reverse DNS Analysis\n")
        f.write("=======================\n\n")
        
        matching = sum(1 for ip in results if results[ip]["matches"])
        f.write(f"Total IPs processed: {len(results)}\n")
        f.write(f"IPs with matching reverse DNS: {matching}\n\n")
        
        f.write("Detailed Results:\n")
        for ip in results:
            f.write(f"\nIP: {ip}\n")
            f.write(f"Expected reverse: {results[ip]['expected_reverse']}\n")
            f.write(f"Found reverse: {results[ip]['found_reverse']}\n")
            f.write(f"Matches: {results[ip]['matches']}\n")
            if results[ip]["error"]:
                f.write(f"Error: {results[ip]['error']}\n")
    
    print(f"\nResults saved to {json_file}")
    print(f"Report saved to {output_file}")

if __name__ == "__main__":
    INPUT_FILE = "ips.txt"
    JSON_FILE = "dig_results.json"
    OUTPUT_FILE = "dig_analysis.txt"
    
    process_ips(INPUT_FILE, JSON_FILE, OUTPUT_FILE)
