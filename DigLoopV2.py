import subprocess
import time
import os
from datetime import datetime
from urllib.parse import urlparse

def clean_domain(url):
    """Extract domain from URL, removing https://, paths, and query parameters"""
    # Handle cases where URL doesn't start with http:// or https://
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    return parsed.netloc

def run_dns_queries(input_file, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get current timestamp for file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define output files
    dig_output = os.path.join(output_dir, f"dig_forward_{timestamp}.txt")
    nslookup_output = os.path.join(output_dir, f"nslookup_forward_{timestamp}.txt")
    host_output = os.path.join(output_dir, f"host_forward_{timestamp}.txt")
    
    # Read URLs from input file and clean them to get just domains
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
        domains = [clean_domain(url) for url in urls]
    
    # Create a mapping file to show original URLs and their cleaned domains
    mapping_output = os.path.join(output_dir, f"domain_mapping_{timestamp}.txt")
    with open(mapping_output, 'w') as f:
        f.write("Original URL -> Cleaned Domain\n")
        f.write("-" * 50 + "\n")
        for url, domain in zip(urls, domains):
            f.write(f"{url} -> {domain}\n")
    
    # Run dig queries
    print("Running dig queries...")
    with open(dig_output, 'w') as f:
        for domain in domains:
            try:
                result = subprocess.run(['dig', domain], capture_output=True, text=True)
                f.write(f"\n--- Query for {domain} ---\n")
                f.write(result.stdout)
                f.flush()  # Force write to disk
                time.sleep(10)  # 10 second delay between queries
            except Exception as e:
                f.write(f"\nError querying {domain}: {str(e)}\n")
    
    # Run nslookup queries
    print("Running nslookup queries...")
    with open(nslookup_output, 'w') as f:
        for domain in domains:
            try:
                result = subprocess.run(['nslookup', domain], capture_output=True, text=True)
                f.write(f"\n--- Query for {domain} ---\n")
                f.write(result.stdout)
                f.flush()  # Force write to disk
                time.sleep(10)  # 10 second delay between queries
            except Exception as e:
                f.write(f"\nError querying {domain}: {str(e)}\n")
    
    # Run host queries
    print("Running host queries...")
    with open(host_output, 'w') as f:
        for domain in domains:
            try:
                result = subprocess.run(['host', domain], capture_output=True, text=True)
                f.write(f"\n--- Query for {domain} ---\n")
                f.write(result.stdout)
                f.flush()  # Force write to disk
                time.sleep(10)  # 10 second delay between queries
            except Exception as e:
                f.write(f"\nError querying {domain}: {str(e)}\n")
    
    print(f"\nQueries completed. Results saved in:")
    print(f"Domain mapping: {mapping_output}")
    print(f"dig results: {dig_output}")
    print(f"nslookup results: {nslookup_output}")
    print(f"host results: {host_output}")

if __name__ == "__main__":
    # Replace these paths with your actual paths
    input_file = "iplist.txt"  # File containing list of URLs
    output_dir = "chariot"  # Directory where results will be saved
    
    run_dns_queries(input_file, output_dir)
