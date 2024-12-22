import xml.etree.ElementTree as ET
import os
from pathlib import Path
import shutil
import argparse

class XMLProcessor:
    def __init__(self, xml_file):
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        
        # Create base directories if they don't exist
        self.base_dirs = ['POST', 'PUT', 'GET', 'DELETE', 'Objects', 'Functions']
        for dir_name in self.base_dirs:
            Path(dir_name).mkdir(exist_ok=True)
            
        # Common file extensions to look for
        self.file_extensions = {'.js', '.php', '.txt', '.html', '.asp', '.aspx', '.css', 
                              '.xml', '.json', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
        
        # Authentication-related words to look for
        self.auth_words = {'login', 'signup', 'sign-up', 'log-in', 'authenticate', 'auth',
                          'register', 'signin', 'sign-in', 'logout', 'log-out'}

    def sort_by_method(self):
        """Sort requests by HTTP method (GET, POST, PUT, DELETE)"""
        method_items = {'GET': [], 'POST': [], 'PUT': [], 'DELETE': []}
        
        for item in self.root.findall('.//item'):
            method = item.find('method').text.strip()
            if method in method_items:
                method_items[method].append(item)
        
        # Create separate XML files for each method
        for method, items in method_items.items():
            if items:
                new_root = ET.Element('items')
                for item in items:
                    new_root.append(item)
                tree = ET.ElementTree(new_root)
                tree.write(f"{method}/requests_{method.lower()}.xml")

    def sort_by_filetype_and_api(self):
        """Sort requests by file extension and API endpoints"""
        objects_items = []
        
        for item in self.root.findall('.//item'):
            path = item.find('path').text
            url = item.find('url').text
            
            # Check for file extensions
            has_extension = any(ext in path.lower() for ext in self.file_extensions)
            
            # Check for 'api' in path
            has_api = 'api' in path.lower()
            
            if has_extension or has_api:
                objects_items.append(item)
        
        if objects_items:
            new_root = ET.Element('items')
            for item in objects_items:
                new_root.append(item)
            tree = ET.ElementTree(new_root)
            tree.write("Objects/objects_endpoints.xml")

    def sort_by_api_and_auth(self):
        """Sort requests by API endpoints and authentication-related paths"""
        functions_items = []
        
        for item in self.root.findall('.//item'):
            path = item.find('path').text.lower()
            
            # Check for 'api' in path or auth-related words
            has_api = 'api' in path
            has_auth = any(word in path for word in self.auth_words)
            
            if has_api or has_auth:
                functions_items.append(item)
        
        if functions_items:
            new_root = ET.Element('items')
            for item in functions_items:
                new_root.append(item)
            tree = ET.ElementTree(new_root)
            tree.write("Functions/api_auth_endpoints.xml")

    def process(self):
        """Run all sorting operations"""
        self.sort_by_method()
        self.sort_by_filetype_and_api()
        self.sort_by_api_and_auth()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process XML file and sort requests into categories')
    parser.add_argument('-f', '--file', required=True, help='Input XML file to process')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip cleaning up existing directories')
    args = parser.parse_args()

    # Verify file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        return

    # Clean up existing directories unless --no-cleanup is specified
    if not args.no_cleanup:
        for dir_name in ['POST', 'PUT', 'GET', 'DELETE', 'Objects', 'Functions']:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
            os.makedirs(dir_name)

    try:
        processor = XMLProcessor(args.file)
        processor.process()
        print(f"XML processing complete. Input file: {args.file}")
        print("Check the respective directories for sorted XML files.")
    except ET.ParseError as e:
        print(f"Error: Could not parse XML file: {e}")
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
