import sys
import xml.etree.ElementTree as ET
import os
import shutil
from pathlib import Path
from collections import defaultdict

def create_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_endpoint_path(url):
    """Extract endpoint path from URL"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.path if parsed.path else "/"

def get_filetype(path):
    """Extract filetype from path"""
    ext = Path(path).suffix
    return ext[1:] if ext else "no_extension"

def organize_burp_xml(input_file):
    """Organize Burp Suite XML export into different categories"""
    # Parse XML
    tree = ET.parse(input_file)
    root = tree.getroot()
    
    # Create base directories
    base_dir = "burp_organized"
    directories = {
        "methods": os.path.join(base_dir, "Method"),
        "endpoints": os.path.join(base_dir, "Endpoints"),
        "filetypes": os.path.join(base_dir, "Filetypes")
    }
    
    for directory in directories.values():
        create_directory(directory)
    
    # Data containers
    methods_data = defaultdict(list)
    endpoints_data = defaultdict(list)
    filetypes_data = defaultdict(list)
    
    # Process each item
    for item in root.findall(".//item"):
        # Extract basic information
        method = item.find("method").text
        url = item.find("url").text
        endpoint = get_endpoint_path(url)
        filetype = get_filetype(endpoint)
        
        # Store item in respective containers
        methods_data[method].append(item)
        endpoints_data[endpoint].append(item)
        filetypes_data[filetype].append(item)
    
    # Create XML files for methods
    for method, items in methods_data.items():
        output_file = os.path.join(directories["methods"], f"{method}.xml")
        create_xml_file(output_file, items)
    
    # Create XML files for endpoints
    for endpoint, items in endpoints_data.items():
        safe_endpoint = "".join(x for x in endpoint if x.isalnum() or x in "._-/")
        safe_endpoint = safe_endpoint.replace("/", "_")
        output_file = os.path.join(directories["endpoints"], f"{safe_endpoint}.xml")
        create_xml_file(output_file, items)
    
    # Create XML files for filetypes
    for filetype, items in filetypes_data.items():
        output_file = os.path.join(directories["filetypes"], f"{filetype}.xml")
        create_xml_file(output_file, items)

def create_xml_file(output_file, items):
    """Create XML file with given items"""
    # Create root element
    root = ET.Element("items")
    root.set("burpVersion", "2024.5.4")  # You might want to make this dynamic
    
    # Add all items
    for item in items:
        root.append(item)
    
    # Create the XML tree and save
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_xml_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist")
        sys.exit(1)
    
    try:
        organize_burp_xml(input_file)
        print("Organization complete! Check the 'burp_organized' directory.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
