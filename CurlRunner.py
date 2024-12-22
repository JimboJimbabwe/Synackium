import os
import subprocess
from pathlib import Path
import re
import argparse
import gzip
import io

def find_next_response_number(output_dir):
    """Find the next available response number by checking existing files"""
    existing_files = [f for f in output_dir.glob("response*.txt")]
    if not existing_files:
        return 1
        
    numbers = []
    for file in existing_files:
        match = re.search(r'response(\d+)\.txt', file.name)
        if match:
            numbers.append(int(match.group(1)))
            
    return max(numbers) + 1 if numbers else 1

def is_gzipped(content):
    """Check if content is gzipped by looking at magic numbers"""
    return len(content) > 2 and content[0] == 0x1f and content[1] == 0x8b

def decode_response(raw_content):
    """Decode response content, handling gzip if necessary"""
    try:
        # First try to split headers from body
        parts = raw_content.split(b'\r\n\r\n', 1)
        
        if len(parts) < 2:
            # No clear header/body split, return as-is
            return raw_content.decode('utf-8', errors='replace')
            
        headers, body = parts
        
        # Decode headers normally
        headers_text = headers.decode('utf-8', errors='replace')
        
        # Check if body is gzipped
        if is_gzipped(body):
            try:
                body_text = gzip.decompress(body).decode('utf-8', errors='replace')
            except Exception as e:
                body_text = f"[Error decompressing gzipped content: {str(e)}]"
        else:
            body_text = body.decode('utf-8', errors='replace')
            
        return f"{headers_text}\r\n\r\n{body_text}"
        
    except Exception as e:
        return f"[Error decoding response: {str(e)}]"

def process_curl_command(input_file, output_dir):
    """Process a curl command from input file and save response"""
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Read curl command
        with open(input_file, 'r') as f:
            curl_command = f.read().strip()
        
        # Find next available response number
        response_num = find_next_response_number(output_dir)
        output_file = output_dir / f"response{response_num}.txt"
        
        # Execute curl command and capture raw output
        result = subprocess.run(
            ['bash', '-c', curl_command],
            capture_output=True
        )
        
        # Save response, handling potential gzipped content
        with open(output_file, 'w', encoding='utf-8') as f:
            if result.stdout:
                decoded_output = decode_response(result.stdout)
                f.write(decoded_output)
            if result.stderr:
                f.write(f"\n--- Error Output ---\n{result.stderr.decode('utf-8', errors='replace')}")
                
        print(f"Response saved to: {output_file}")
        
        # Save the original request too
        request_file = output_dir / f"request{response_num}.txt"
        with open(request_file, 'w', encoding='utf-8') as f:
            f.write(curl_command)
        print(f"Request saved to: {request_file}")
        
        # Check if command was successful
        if result.returncode != 0:
            print(f"Warning: Curl command returned non-zero exit code: {result.returncode}")
            
    except Exception as e:
        print(f"Error processing curl command: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Run curl commands from file and save responses')
    parser.add_argument('input_file', help='Input file containing curl command')
    parser.add_argument('--output-dir', '-o', default='./responses',
                      help='Output directory for responses (default: ./responses)')
                      
    args = parser.parse_args()
    
    try:
        process_curl_command(args.input_file, args.output_dir)
    except Exception as e:
        print(f"Failed to process curl command: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
