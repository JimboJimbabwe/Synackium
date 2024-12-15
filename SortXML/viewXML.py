import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import base64
from pathlib import Path

class HTTPViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Request/Response Viewer")
        self.root.geometry("1200x800")
        
        # Data
        self.current_index = 0
        self.items = []
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Navigation frame
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.prev_button = ttk.Button(nav_frame, text="← Previous", command=self.previous_item)
        self.prev_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.next_item)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.counter_label = ttk.Label(nav_frame, text="")
        self.counter_label.pack(side=tk.LEFT, padx=10)
        
        # Request Frame
        req_frame = ttk.LabelFrame(main_frame, text="Request", padding="5")
        req_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Request URL
        self.url_label = ttk.Label(req_frame, text="URL:", wraplength=550)
        self.url_label.pack(fill=tk.X, pady=(0, 5))
        
        # Request Headers
        self.req_text = tk.Text(req_frame, wrap=tk.WORD, width=60, height=30)
        self.req_text.pack(fill=tk.BOTH, expand=True)
        req_scroll = ttk.Scrollbar(req_frame, orient=tk.VERTICAL, command=self.req_text.yview)
        req_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.req_text['yscrollcommand'] = req_scroll.set
        
        # Response Frame
        resp_frame = ttk.LabelFrame(main_frame, text="Response", padding="5")
        resp_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Response Status
        self.status_label = ttk.Label(resp_frame, text="Status:")
        self.status_label.pack(fill=tk.X, pady=(0, 5))
        
        # Response Headers
        self.resp_text = tk.Text(resp_frame, wrap=tk.WORD, width=60, height=30)
        self.resp_text.pack(fill=tk.BOTH, expand=True)
        resp_scroll = ttk.Scrollbar(resp_frame, orient=tk.VERTICAL, command=self.resp_text.yview)
        resp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.resp_text['yscrollcommand'] = resp_scroll.set
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Bind keyboard shortcuts
        root.bind('<Left>', lambda e: self.previous_item())
        root.bind('<Right>', lambda e: self.next_item())
        
        # Style configuration
        style = ttk.Style()
        style.configure('TLabelframe', padding=5)
        style.configure('TLabelframe.Label', font=('Helvetica', 10, 'bold'))
        
    def load_xml_file(self, filename):
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
        try:
            return base64.b64decode(content).decode('utf-8')
        except:
            return "Unable to decode base64 content"
    
    def update_display(self):
        item = self.items[self.current_index]
        
        # Update counter
        self.counter_label.config(text=f"Request {self.current_index + 1} of {len(self.items)}")
        
        # Update URL
        url = item.find('url').text
        self.url_label.config(text=f"URL: {url}")
        
        # Update status
        status = item.find('status').text
        self.status_label.config(text=f"Status: {status}")
        
        # Update request
        request = item.find('request')
        request_content = request.text
        if request.get('base64') == 'true':
            request_content = self.decode_base64(request_content)
        
        self.req_text.delete('1.0', tk.END)
        self.req_text.insert('1.0', request_content)
        
        # Update response
        response = item.find('response')
        response_content = response.text
        if response.get('base64') == 'true':
            response_content = self.decode_base64(response_content)
        
        self.resp_text.delete('1.0', tk.END)
        self.resp_text.insert('1.0', response_content)
        
        # Update button states
        self.prev_button.state(['!disabled'] if self.current_index > 0 else ['disabled'])
        self.next_button.state(['!disabled'] if self.current_index < len(self.items) - 1 else ['disabled'])
    
    def previous_item(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
    
    def next_item(self):
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            self.update_display()

def main():
    root = tk.Tk()
    app = HTTPViewer(root)
    
    # If you want to automatically load a file, uncomment and modify the following line:
    # app.load_xml_file("your_file.xml")
    
    root.mainloop()

if __name__ == "__main__":
    main()
