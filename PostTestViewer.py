import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import re
from datetime import datetime
import json

class HTTPFolderViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Request/Response Folder Viewer")
        self.root.geometry("1200x800")
        
        # Data storage
        self.current_index = 0
        self.request_response_pairs = []  # List of tuples (request_file, response_file)
        self.working_dir = None
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup all GUI elements"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.setup_navigation_frame()
        self.setup_folder_frame()
        self.setup_display_frames()
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

    def setup_navigation_frame(self):
        """Setup navigation buttons and counter"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.prev_button = ttk.Button(nav_frame, text="← Previous", command=self.previous_pair)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.next_pair)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.counter_label = ttk.Label(nav_frame, text="")
        self.counter_label.pack(side=tk.LEFT, padx=10)
        
        self.refresh_button = ttk.Button(nav_frame, text="🔄 Refresh", command=self.refresh_files)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)

    def setup_folder_frame(self):
        """Setup folder selection"""
        folder_frame = ttk.Frame(self.main_frame)
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(folder_frame, text="Working Directory:").pack(side=tk.LEFT)
        self.folder_path_entry = ttk.Entry(folder_frame, width=50)
        self.folder_path_entry.pack(side=tk.LEFT, padx=5)
        
        browse_button = ttk.Button(folder_frame, text="Browse...", command=self.browse_folder)
        browse_button.pack(side=tk.LEFT)
        
    def setup_display_frames(self):
        """Setup request and response display areas"""
        # Request Frame
        req_frame = ttk.LabelFrame(self.main_frame, text="Request", padding="5")
        req_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.req_text = tk.Text(req_frame, wrap=tk.WORD, width=60, height=30)
        self.req_text.pack(fill=tk.BOTH, expand=True)
        req_scroll = ttk.Scrollbar(req_frame, orient=tk.VERTICAL, command=self.req_text.yview)
        req_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.req_text['yscrollcommand'] = req_scroll.set
        
        # Response Frame
        resp_frame = ttk.LabelFrame(self.main_frame, text="Response", padding="5")
        resp_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.resp_text = tk.Text(resp_frame, wrap=tk.WORD, width=60, height=30)
        self.resp_text.pack(fill=tk.BOTH, expand=True)
        resp_scroll = ttk.Scrollbar(resp_frame, orient=tk.VERTICAL, command=self.resp_text.yview)
        resp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.resp_text['yscrollcommand'] = resp_scroll.set

    def browse_folder(self):
        """Open folder browser dialog"""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.working_dir = Path(dir_path)
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, str(self.working_dir))
            self.refresh_files()
            
    def find_request_response_pairs(self):
        """Find and pair request/response files in the working directory"""
        self.request_response_pairs = []
        if not self.working_dir:
            return
            
        # Find all request and response files
        files = list(self.working_dir.glob("*.txt"))
        request_files = sorted([f for f in files if f.name.startswith("request")])
        response_files = sorted([f for f in files if f.name.startswith("response")])
        
        # Match them by number
        for req_file in request_files:
            req_num = re.search(r'request(\d+)\.txt', req_file.name)
            if req_num:
                num = req_num.group(1)
                resp_file = self.working_dir / f"response{num}.txt"
                if resp_file in response_files:
                    self.request_response_pairs.append((req_file, resp_file))
        
        # Sort pairs by number
        self.request_response_pairs.sort(key=lambda x: int(re.search(r'request(\d+)\.txt', x[0].name).group(1)))
        
    def refresh_files(self):
        """Refresh the file list and update display"""
        if not self.working_dir:
            return
            
        self.find_request_response_pairs()
        self.current_index = 0
        self.update_display()
        
    def update_display(self):
        """Update the display with current request/response pair"""
        # Clear displays
        self.req_text.delete('1.0', tk.END)
        self.resp_text.delete('1.0', tk.END)
        
        if not self.request_response_pairs:
            self.counter_label.config(text="No request/response pairs found")
            return
            
        # Update counter
        self.counter_label.config(text=f"Pair {self.current_index + 1} of {len(self.request_response_pairs)}")
        
        # Get current pair
        req_file, resp_file = self.request_response_pairs[self.current_index]
        
        # Load request
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                self.req_text.insert('1.0', f.read())
        except Exception as e:
            self.req_text.insert('1.0', f"Error loading request: {str(e)}")
            
        # Load response
        try:
            with open(resp_file, 'r', encoding='utf-8') as f:
                self.resp_text.insert('1.0', f.read())
        except Exception as e:
            self.resp_text.insert('1.0', f"Error loading response: {str(e)}")
            
        # Update button states
        self.prev_button.state(['!disabled'] if self.current_index > 0 else ['disabled'])
        self.next_button.state(['!disabled'] if self.current_index < len(self.request_response_pairs) - 1 else ['disabled'])
        
    def previous_pair(self):
        """Show previous request/response pair"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            
    def next_pair(self):
        """Show next request/response pair"""
        if self.current_index < len(self.request_response_pairs) - 1:
            self.current_index += 1
            self.update_display()

def main():
    root = tk.Tk()
    app = HTTPFolderViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
