import re
import sys
from pathlib import Path
import argparse

def extract_cookies(content):
    """Extract Set-Cookie headers from HTTP response"""
    # Using regex to find Set-Cookie headers
    # Case insensitive match for "Set-Cookie:" followed by any characters until newline
    cookie_pattern = re.compile(r'^Set-Cookie:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    return cookie_pattern.findall(content)

def save_cookies(cookies, output_file):
    """Save extracted cookies to a file"""
    try:
        with open(output_file, 'w') as f:
            for cookie in cookies:
                f.write(f"{cookie}\n")
        print(f"Successfully saved {len(cookies)} cookies to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def read_http_file(input_file):
    """Read content from input file"""
    try:
        with open(input_file, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Extract Set-Cookie headers from HTTP response')
    parser.add_argument('input_file', help='Input file containing HTTP response')
    parser.add_argument('-o', '--output', default='cookies.txt', 
                       help='Output file for cookies (default: cookies.txt)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Read content
    content = read_http_file(args.input_file)
    
    # Extract cookies
    cookies = extract_cookies(content)
    
    if not cookies:
        print("No Set-Cookie headers found in input file")
        sys.exit(0)
    
    # Save cookies
    save_cookies(cookies, args.output)

if __name__ == "__main__":
    main()