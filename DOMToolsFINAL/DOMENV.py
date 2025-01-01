import xml.etree.ElementTree as ET
import os

def parse_burp_xml(xml_content):
    # Parse XML
    root = ET.fromstring(xml_content)
    
    # Extract URLs and create folders
    urls = []
    for item in root.findall('item'):
        url = item.find('url').text
        urls.append(url)
        
        # Get path and create folder
        path = item.find('path').text.strip('/')
        if path:
            # Replace slashes with hyphens
            folder_name = path.replace('/', '-')
            os.makedirs(folder_name, exist_ok=True)
    
    # Write URLs to file
    with open('URLs.txt', 'w') as f:
        for url in urls:
            f.write(f"{url}\n")

# Read XML file
with open('DOMTest.xml', 'r') as f:
    xml_content = f.read()

parse_burp_xml(xml_content)