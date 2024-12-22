import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
import base64
from pathlib import Path
import re
from datetime import datetime
import os

class HTTPViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Request/Response Viewer")
        self.root.geometry("1200x800")
        
        # Data
        self.current_index = 0
        self.items = []
        self.current_item = None
        self.output_dir = Path.home() / "http_viewer_output"  # Default output directory
        
        self.setup_gui()
        self.setup_bindings()
        
    def setup_gui(self):
        """Setup all GUI elements"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup all sub-frames
        self.setup_navigation_frame()
        self.setup_output_frame()
        self.setup_url_frame()
        self.setup_request_frame()
        self.setup_response_frame()
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
    def setup_navigation_frame(self):
        """Setup navigation buttons and counter"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.prev_button = ttk.Button(nav_frame, text="← Previous", command=self.previous_item)
        self.prev_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.next_item)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.counter_label = ttk.Label(nav_frame, text="")
        self.counter_label.pack(side=tk.LEFT, padx=10)
        
        self.save_button = ttk.Button(nav_frame, text="Save as Curl", command=self.save_as_curl)
        self.save_button.pack(side=tk.RIGHT)
        
    def setup_output_frame(self):
        """Setup output directory configuration"""
        output_frame = ttk.Frame(self.main_frame)
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.output_path_entry = ttk.Entry(output_frame, width=50)
        self.output_path_entry.pack(side=tk.LEFT, padx=5)
        self.output_path_entry.insert(0, str(self.output_dir))
        
        browse_button = ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir)
        browse_button.pack(side=tk.LEFT)
        
    def setup_url_frame(self):
        """Setup URL and endpoint input fields"""
        url_frame = ttk.Frame(self.main_frame)
        url_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Base URL
        ttk.Label(url_frame, text="Base URL:").pack(side=tk.LEFT)
        self.base_url_entry = ttk.Entry(url_frame, width=50)
        self.base_url_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Endpoint
        ttk.Label(url_frame, text="Endpoint:").pack(side=tk.LEFT)
        self.endpoint_entry = ttk.Entry(url_frame, width=30)
        self.endpoint_entry.pack(side=tk.LEFT, padx=5)
        
    def setup_request_frame(self):
        """Setup request display area"""
        req_frame = ttk.LabelFrame(self.main_frame, text="Request", padding="5")
        req_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.req_text = tk.Text(req_frame, wrap=tk.WORD, width=60, height=30)
        self.req_text.pack(fill=tk.BOTH, expand=True)
        req_scroll = ttk.Scrollbar(req_frame, orient=tk.VERTICAL, command=self.req_text.yview)
        req_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.req_text['yscrollcommand'] = req_scroll.set
        
    def setup_response_frame(self):
        """Setup response display area"""
        resp_frame = ttk.LabelFrame(self.main_frame, text="Response", padding="5")
        resp_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_label = ttk.Label(resp_frame, text="Status:")
        self.status_label.pack(fill=tk.X, pady=(0, 5))
        
        self.resp_text = tk.Text(resp_frame, wrap=tk.WORD, width=60, height=30)
        self.resp_text.pack(fill=tk.BOTH, expand=True)
        resp_scroll = ttk.Scrollbar(resp_frame, orient=tk.VERTICAL, command=self.resp_text.yview)
        resp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.resp_text['yscrollcommand'] = resp_scroll.set
        
    def setup_bindings(self):
        """Setup all event bindings"""
        self.root.bind('<Left>', lambda e: self.previous_item())
        self.root.bind('<Right>', lambda e: self.next_item())
        self.base_url_entry.bind('<KeyRelease>', self.on_url_change)
        self.endpoint_entry.bind('<KeyRelease>', self.on_url_change)
        
    def browse_output_dir(self):
        """Open directory browser dialog"""
        dir_path = filedialog.askdirectory(initialdir=self.output_dir)
        if dir_path:
            self.output_dir = Path(dir_path)
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, str(self.output_dir))
            
    def generate_filename(self, prefix="curl", extension=".txt"):
        """Generate a unique filename for output"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        method = "unknown"
        endpoint = "unknown"
        
        # Try to extract method and endpoint from request
        if self.current_item:
            request_content = self.req_text.get('1.0', tk.END).strip()
            if request_content:
                first_line = request_content.split('\n')[0]
                method_match = re.match(r'^(\w+)', first_line)
                if method_match:
                    method = method_match.group(1).lower()
                
                endpoint = self.endpoint_entry.get().strip('/')
                if endpoint:
                    # Replace special characters with underscores
                    endpoint = re.sub(r'[^\w-]', '_', endpoint)
                    endpoint = re.sub(r'_+', '_', endpoint)  # Replace multiple underscores with single
                    endpoint = endpoint[:30]  # Limit length
        
        return f"{prefix}_{method}_{endpoint}_{timestamp}{extension}"
        
    def on_url_change(self, event=None):
        """Handle URL or endpoint changes"""
        if self.current_item is not None:
            full_url = self.get_full_url()
            url_elem = self.current_item.find('url')
            if url_elem is not None:
                url_elem.text = full_url
                
    def get_full_url(self):
        """Combine base URL and endpoint"""
        base_url = self.base_url_entry.get().rstrip('/')
        endpoint = self.endpoint_entry.get()
        if endpoint and not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return base_url + endpoint
        
    def split_url(self, url):
        """Split URL into base and endpoint"""
        if not url:
            return '', ''
        
        # Find the last occurrence of / before any query parameters
        base_end = url.find('?')
        if base_end == -1:
            base_end = len(url)
            
        last_slash = url.rfind('/', 0, base_end)
        
        if last_slash == -1:
            return url, ''
        else:
            base_url = url[:last_slash]
            endpoint = url[last_slash:]
            return base_url, endpoint
            
    def load_xml_file(self, filename):
        """Load and parse XML file"""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            self.items = root.findall('.//item')
            if self.items:
                self.update_display()
            else:
                messagebox.showerror("Error", "No items found in XML file")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load XML file: {str(e)}")
            
    def decode_base64(self, content):
        """Decode base64 content"""
        try:
            return base64.b64decode(content).decode('utf-8')
        except:
            return "Unable to decode base64 content"
            
    def update_display(self):
        """Update all display elements with current item data"""
        self.current_item = self.items[self.current_index]
        
        # Update counter
        self.counter_label.config(text=f"Request {self.current_index + 1} of {len(self.items)}")
        
        # Update URL fields
        url = self.current_item.find('url').text
        base_url, endpoint = self.split_url(url)
        self.base_url_entry.delete(0, tk.END)
        self.base_url_entry.insert(0, base_url)
        self.endpoint_entry.delete(0, tk.END)
        self.endpoint_entry.insert(0, endpoint)
        
        # Update status
        status = self.current_item.find('status').text
        self.status_label.config(text=f"Status: {status}")
        
        # Update request
        request = self.current_item.find('request')
        request_content = request.text
        if request.get('base64') == 'true':
            request_content = self.decode_base64(request_content)
        
        self.req_text.delete('1.0', tk.END)
        self.req_text.insert('1.0', request_content)
        
        # Update response
        response = self.current_item.find('response')
        response_content = response.text
        if response.get('base64') == 'true':
            response_content = self.decode_base64(response_content)
        
        self.resp_text.delete('1.0', tk.END)
        self.resp_text.insert('1.0', response_content)
        
        # Update button states
        self.prev_button.state(['!disabled'] if self.current_index > 0 else ['disabled'])
        self.next_button.state(['!disabled'] if self.current_index < len(self.items) - 1 else ['disabled'])
        
    def format_curl_command(self, request_content, url):
        """Format request details into a curl command"""
        try:
            # Split request into lines
            lines = request_content.split('\n')
            method = lines[0].split()[0]
            headers = ["-H $'synack-WalkerTXSSRanger: 1'"]
            cookie = None
            
            # Parse headers
            for line in lines[1:]:
                if not line.strip():
                    continue
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key.lower() == 'cookie':
                        cookie = value
                    elif key.lower() not in ['connection', 'content-length']:
                        headers.append(f"-H $'{key}: {value}'")
            
            # Build curl command
            curl_parts = [f"curl --path-as-is -i -s -k -X $'{method}'"]
            curl_parts.extend(f"    {header}" for header in sorted(headers))
            
            if cookie:
                curl_parts.append(f"    -b $'{cookie}'")
            
            curl_parts.append(f"    $'{url}'")
            
            return ' \\\n'.join(curl_parts)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format curl command: {str(e)}")
            return None
            
    def save_as_curl(self):
        """Save current request as curl command"""
        try:
            if not self.current_item:
                return
            
            # Ensure output directory exists
            output_dir = Path(self.output_path_entry.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            request_content = self.req_text.get('1.0', tk.END).strip()
            url = self.get_full_url()
            
            curl_command = self.format_curl_command(request_content, url)
            if curl_command:
                output_file = output_dir / self.generate_filename()
                with open(output_file, 'w') as f:
                    f.write(curl_command)
                messagebox.showinfo("Success", f"Curl command saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save curl command: {str(e)}")
            
    def previous_item(self):
        """Navigate to previous item"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            
    def next_item(self):
        """Navigate to next item"""
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            self.update_display()
            
def main():
    root = tk.Tk()
    app = HTTPViewer(root)
    app.load_xml_file("NBA.xml")
    root.mainloop()

if __name__ == "__main__":
    main()
