import xml.etree.ElementTree as ET
import base64
import random
import re

def decode_base64(encoded_str):
    """Decode base64 string and return decoded bytes."""
    try:
        return base64.b64decode(encoded_str)
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return None

def parse_request(request_bytes):
    """Parse raw HTTP request into components."""
    try:
        # Split request into lines and remove empty lines
        request_lines = [line for line in request_bytes.decode('utf-8').split('\n') if line.strip()]
        
        # Parse first line for method, path, and HTTP version
        method, path, version = request_lines[0].strip().split(' ')
        
        # Parse headers
        headers = {}
        for line in request_lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
            
        return {
            'method': method,
            'path': path,
            'version': version,
            'headers': headers
        }
    except Exception as e:
        print(f"Error parsing request: {e}")
        return None

def format_curl_command(url, method, headers):
    """Format request details into a curl command exactly matching Burp format."""
    curl_parts = [f"curl --path-as-is -i -s -k -X $'{method}'"]
    
    cookie = None
    header_lines = []
    
    # Process headers
    for header, value in headers.items():
        # Skip Connection and Content-Length headers
        if header.lower() in ['connection', 'content-length']:
            continue
        # Handle Cookie separately
        if header.lower() == 'cookie':
            cookie = value
            continue
        # Add other headers
        header_lines.append(f"    -H $'{header}: {value}'")
    
    # Sort headers for consistency (except Cookie)
    curl_parts.extend(sorted(header_lines))
    
    # Add cookie if present
    if cookie:
        curl_parts.append(f"    -b $'{cookie}'")
    
    # Add URL
    curl_parts.append(f"    $'{url}'")
    
    return ' \\\n'.join(curl_parts)

def process_burp_xml(xml_file):
    """Process Burp XML file and return a random request as curl command."""
    try:
        # Parse XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all items with requests
        items = root.findall('.//item')
        if not items:
            raise Exception("No request items found in XML")
            
        # Select random item
        item = random.choice(items)
        
        # Get URL components
        protocol = item.find('protocol').text
        host = item.find('host').text
        port = item.find('port').text
        path = item.find('path').text
        
        # Construct full URL
        url = f"{protocol}://{host}"
        if (protocol == 'https' and port != '443') or (protocol == 'http' and port != '80'):
            url += f":{port}"
        url += path
        
        # Get request details
        request_elem = item.find('request')
        if request_elem is None:
            raise Exception("No request element found")
            
        # Check if base64 encoded
        is_base64 = request_elem.get('base64', 'false') == 'true'
        request_data = request_elem.text
        
        if not request_data:
            raise Exception("Empty request data")
            
        # Decode if needed
        if is_base64:
            decoded_request = decode_base64(request_data)
            if not decoded_request:
                raise Exception("Failed to decode base64 request")
        else:
            decoded_request = request_data.encode('utf-8')
            
        # Parse request
        parsed_request = parse_request(decoded_request)
        if not parsed_request:
            raise Exception("Failed to parse request")
            
        # Format curl command
        curl_cmd = format_curl_command(url, parsed_request['method'], parsed_request['headers'])
        
        return curl_cmd
        
    except Exception as e:
        print(f"Error processing XML: {e}")
        return None

def main():
    """Main function to process XML file and save curl command."""
    xml_file = 'NBA.xml'  # Input XML file
    output_file = 'curl_3.txt'  # Output file for curl command
    
    try:
        curl_cmd = process_burp_xml(xml_file)
        if curl_cmd:
            with open(output_file, 'w') as f:
                f.write(curl_cmd)
            print(f"Curl command has been saved to {output_file}")
        else:
            print("Failed to generate curl command")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
