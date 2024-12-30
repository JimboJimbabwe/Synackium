import xml.etree.ElementTree as ET
import base64
import os
import argparse
from pathlib import Path
import re

class BurpExtractor:
    def __init__(self, output_dir="output"):
        """Initialize with output directory"""
        self.output_dir = Path(output_dir)
        self.create_output_dirs()
        
    def create_output_dirs(self):
        """Create output directories if they don't exist"""
        # Create main output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for each type
        (self.output_dir / "requests").mkdir(exist_ok=True)
        (self.output_dir / "responses").mkdir(exist_ok=True)
        (self.output_dir / "referrers").mkdir(exist_ok=True)
        
    def decode_base64(self, content):
        """Decode base64 content, handling errors"""
        try:
            return base64.b64decode(content).decode('utf-8', errors='replace')
        except Exception as e:
            return f"Error decoding content: {str(e)}"
            
    def extract_referrer(self, request_text):
        """Extract referrer from request headers"""
        referrer_match = re.search(r'Referer:\s*([^\r\n]+)', request_text, re.IGNORECASE)
        return referrer_match.group(1) if referrer_match else "No Referrer"
        
    def save_content(self, content, filename):
        """Save content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error saving {filename}: {str(e)}")
            
    def process_xml(self, xml_file):
        """Process Burp XML file and extract items"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Process each item
            for idx, item in enumerate(root.findall('.//item'), 1):
                print(f"Processing item {idx}...")
                
                # Extract request
                request = item.find('request')
                if request is not None:
                    request_content = self.decode_base64(request.text) if request.get('base64') == 'true' else request.text
                    self.save_content(request_content, self.output_dir / "requests" / f"Req{idx}.txt")
                    
                    # Extract and save referrer
                    referrer = self.extract_referrer(request_content)
                    self.save_content(referrer, self.output_dir / "referrers" / f"Ref{idx}.txt")
                
                # Extract response
                response = item.find('response')
                if response is not None:
                    response_content = self.decode_base64(response.text) if response.get('base64') == 'true' else response.text
                    self.save_content(response_content, self.output_dir / "responses" / f"Resp{idx}.txt")
                
            print(f"\nExtraction complete! Files saved in {self.output_dir}")
            
        except ET.ParseError as e:
            print(f"Error parsing XML file: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Extract requests, responses, and referrers from Burp XML')
    parser.add_argument('xml_file', help='Input Burp XML file')
    parser.add_argument('-o', '--output', default='output',
                      help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.xml_file).exists():
        print(f"Error: Input file '{args.xml_file}' does not exist")
        return
    
    # Process the XML file
    extractor = BurpExtractor(args.output)
    extractor.process_xml(args.xml_file)

if __name__ == "__main__":
    main()