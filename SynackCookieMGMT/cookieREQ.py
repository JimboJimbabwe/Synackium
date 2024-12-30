import json
import urllib.parse
from datetime import datetime
import argparse
import sys
from pathlib import Path

def read_cookie_file(filepath):
    """Read cookies from a text file"""
    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading file {filepath}: {str(e)}")
        sys.exit(1)

def parse_cookies(cookie_string):
    """Parse cookie string and return formatted output"""
    cookies = []
    
    # Split cookies
    for cookie in cookie_string.split(';'):
        if '=' in cookie:
            try:
                name, value = cookie.strip().split('=', 1)
                
                # Try to decode and format value
                try:
                    decoded_value = urllib.parse.unquote(value)
                    try:
                        # Try to parse as JSON
                        json_value = json.loads(decoded_value)
                        formatted_value = json.dumps(json_value, indent=2)
                    except:
                        formatted_value = decoded_value
                except:
                    formatted_value = value
                    
                cookies.append({
                    'name': name.strip(),
                    'value': formatted_value,
                    'length': len(value.strip()),
                    'raw_value': value.strip()  # Store raw value for reference
                })
            except Exception as e:
                print(f"Warning: Could not parse cookie: {cookie}")
                continue
    
    return cookies

def print_cookies(cookies, output_file=None):
    """Print cookies in a formatted way, optionally to a file"""
    output = []
    output.append("\n=== Cookie Analysis ===")
    output.append(f"Total Cookies Found: {len(cookies)}\n")
    
    for i, cookie in enumerate(cookies, 1):
        output.append(f"Cookie #{i}:")
        output.append(f"Name: {cookie['name']}")
        output.append(f"Length: {cookie['length']} characters")
        output.append("Value:")
        output.append("-" * 50)
        output.append(cookie['value'])
        output.append("Raw Value:")
        output.append(cookie['raw_value'])
        output.append("=" * 50 + "\n")
    
    output_text = '\n'.join(output)
    
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(output_text)
            print(f"Results written to {output_file}")
        except Exception as e:
            print(f"Error writing to output file: {str(e)}")
            print(output_text)
    else:
        print(output_text)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Cookie Parser - Read and analyze cookies from a text file')
    parser.add_argument('input_file', help='Path to the input file containing cookies')
    parser.add_argument('-o', '--output', help='Optional output file for results')
    parser.add_argument('--raw', action='store_true', help='Include raw (unformatted) values in output')
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)
    
    # Read cookies from file
    cookie_string = read_cookie_file(args.input_file)
    
    # Parse cookies
    cookies = parse_cookies(cookie_string)
    
    # Print results
    print_cookies(cookies, args.output)

if __name__ == "__main__":
    main()