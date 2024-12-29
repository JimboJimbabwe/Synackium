import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
import base64
from pathlib import Path
import re
from datetime import datetime
import os
import sys
import argparse

class HTTPComparisonViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Request/Response Comparison Viewer")
        self.root.geometry("1400x900")
        
        # Data
        self.requests = []
        self.responses = []
        self.current_request_index = 0
        self.current_response_index = 0
        self.output_dir = Path.home() / "http_viewer_output"
        
        self.setup_gui()
        self.setup_bindings()
        
    def setup_gui(self):
        """Setup all GUI elements"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_navigation_frame()
        self.setup_url_frames()
        self.setup_comparison_frame()
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
    def setup_navigation_frame(self):
        """Setup navigation controls for both request and response"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Request navigation
        req_nav = ttk.LabelFrame(nav_frame, text="Request Navigation", padding="5")
        req_nav.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(req_nav, text="← Prev Request", command=self.prev_request).pack(side=tk.LEFT)
        ttk.Button(req_nav, text="Next Request →", command=self.next_request).pack(side=tk.LEFT, padx=5)
        self.req_counter = ttk.Label(req_nav, text="Request: 0/0")
        self.req_counter.pack(side=tk.LEFT, padx=10)
        
        # Response navigation
        resp_nav = ttk.LabelFrame(nav_frame, text="Response Navigation", padding="5")
        resp_nav.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(resp_nav, text="← Prev Response", command=self.prev_response).pack(side=tk.LEFT)
        ttk.Button(resp_nav, text="Next Response →", command=self.next_response).pack(side=tk.LEFT, padx=5)
        self.resp_counter = ttk.Label(resp_nav, text="Response: 0/0")
        self.resp_counter.pack(side=tk.LEFT, padx=10)
        
    def setup_url_frames(self):
        """Setup URL display for both request and response"""
        # Request URL frame
        req_url_frame = ttk.LabelFrame(self.main_frame, text="Request URL", padding="5")
        req_url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(req_url_frame, text="Endpoint:").pack(side=tk.LEFT)
        self.req_url_entry = ttk.Entry(req_url_frame, width=100)
        self.req_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Response URL frame
        resp_url_frame = ttk.LabelFrame(self.main_frame, text="Response URL", padding="5")
        resp_url_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(resp_url_frame, text="Endpoint:").pack(side=tk.LEFT)
        self.resp_url_entry = ttk.Entry(resp_url_frame, width=100)
        self.resp_url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
    def setup_comparison_frame(self):
        """Setup the main comparison view"""
        comp_frame = ttk.Frame(self.main_frame)
        comp_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Request frame
        req_frame = ttk.LabelFrame(comp_frame, text="Request", padding="5")
        req_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.req_text = tk.Text(req_frame, wrap=tk.WORD, width=70, height=35)
        self.req_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        req_scroll = ttk.Scrollbar(req_frame, orient=tk.VERTICAL, command=self.req_text.yview)
        req_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.req_text['yscrollcommand'] = req_scroll.set
        
        # Response frame
        resp_frame = ttk.LabelFrame(comp_frame, text="Response", padding="5")
        resp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.resp_text = tk.Text(resp_frame, wrap=tk.WORD, width=70, height=35)
        self.resp_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        resp_scroll = ttk.Scrollbar(resp_frame, orient=tk.VERTICAL, command=self.resp_text.yview)
        resp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.resp_text['yscrollcommand'] = resp_scroll.set
        
        # Configure text highlighting
        self.req_text.tag_configure('highlight', background='yellow')
        self.resp_text.tag_configure('match', background='lightgreen')
        
    def setup_bindings(self):
        """Setup event bindings"""
        # Navigation bindings
        self.root.bind('<Control-Left>', lambda e: self.prev_request())
        self.root.bind('<Control-Right>', lambda e: self.next_request())
        self.root.bind('<Alt-Left>', lambda e: self.prev_response())
        self.root.bind('<Alt-Right>', lambda e: self.next_response())
        
        # Text selection binding for comparison
        self.req_text.bind('<<Selection>>', self.handle_selection)
        
    def handle_selection(self, event=None):
        """Handle text selection in request window"""
        try:
            # Get selected text from request
            selected = self.req_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if not selected:
                return
                
            # Remove existing highlights in response
            self.resp_text.tag_remove('match', '1.0', tk.END)
            
            # Search for matches in response
            response_text = self.resp_text.get('1.0', tk.END)
            start_idx = '1.0'
            
            while True:
                match_idx = self.resp_text.search(selected, start_idx, tk.END)
                if not match_idx:
                    break
                    
                # Calculate end index
                end_idx = f"{match_idx}+{len(selected)}c"
                
                # Highlight match
                self.resp_text.tag_add('match', match_idx, end_idx)
                
                # Move start index
                start_idx = end_idx
                
        except tk.TclError:
            # Selection was removed
            pass
            
    def load_xml_file(self, filename):
        """Load and parse XML file"""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Separate requests and responses
            for item in root.findall('.//item'):
                request = item.find('request')
                response = item.find('response')
                url = item.find('url').text
                
                if request is not None:
                    self.requests.append({
                        'url': url,
                        'content': self.decode_base64(request.text) if request.get('base64') == 'true' else request.text
                    })
                    
                if response is not None:
                    self.responses.append({
                        'url': url,
                        'content': self.decode_base64(response.text) if response.get('base64') == 'true' else response.text,
                        'status': item.find('status').text
                    })
                    
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load XML file: {str(e)}")
            
    def decode_base64(self, content):
        """Decode base64 content"""
        try:
            return base64.b64decode(content).decode('utf-8')
        except:
            return "Unable to decode base64 content"
            
    def update_display(self):
        """Update all display elements"""
        if not self.requests or not self.responses:
            return
            
        # Update request
        request = self.requests[self.current_request_index]
        self.req_url_entry.delete(0, tk.END)
        self.req_url_entry.insert(0, request['url'])
        self.req_text.delete('1.0', tk.END)
        self.req_text.insert('1.0', request['content'])
        
        # Update response
        response = self.responses[self.current_response_index]
        self.resp_url_entry.delete(0, tk.END)
        self.resp_url_entry.insert(0, response['url'])
        self.resp_text.delete('1.0', tk.END)
        self.resp_text.insert('1.0', response['content'])
        
        # Update counters
        self.req_counter.config(text=f"Request: {self.current_request_index + 1}/{len(self.requests)}")
        self.resp_counter.config(text=f"Response: {self.current_response_index + 1}/{len(self.responses)}")
        
    def prev_request(self):
        """Navigate to previous request"""
        if self.current_request_index > 0:
            self.current_request_index -= 1
            self.update_display()
            
    def next_request(self):
        """Navigate to next request"""
        if self.current_request_index < len(self.requests) - 1:
            self.current_request_index += 1
            self.update_display()
            
    def prev_response(self):
        """Navigate to previous response"""
        if self.current_response_index > 0:
            self.current_response_index -= 1
            self.update_display()
            
    def next_response(self):
        """Navigate to next response"""
        if self.current_response_index < len(self.responses) - 1:
            self.current_response_index += 1
            self.update_display()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='HTTP Request/Response Comparison Viewer')
    parser.add_argument('xml_file', help='Path to the XML file containing HTTP requests/responses')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    if not os.path.exists(args.xml_file):
        print(f"Error: File '{args.xml_file}' does not exist", file=sys.stderr)
        sys.exit(1)
        
    root = tk.Tk()
    app = HTTPComparisonViewer(root)
    app.load_xml_file(args.xml_file)
    root.mainloop()

if __name__ == "__main__":
    main()
