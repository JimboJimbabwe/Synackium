import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import re
import os

class ModernStyle:
    """Modern styling constants"""
    BG_COLOR = "#f5f5f5"
    BOX_BG = "#ffffff"
    HEADER_BG = "#1a1a1a"
    HEADER_FG = "#ffffff"
    BUTTON_BG = "#2196F3"
    BUTTON_FG = "#ffffff"
    ACTIVE_BTN_BG = "#1976D2"
    TEXT_COLOR = "#333333"
    BORDER_COLOR = "#e0e0e0"
    HIGHLIGHT_COLOR = "#2196F3"
    FONT_FAMILY = "Helvetica"
    
class ModernButton(tk.Button):
    """Custom button with modern styling"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            bg=ModernStyle.BUTTON_BG,
            fg=ModernStyle.BUTTON_FG,
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=(ModernStyle.FONT_FAMILY, 10),
            activebackground=ModernStyle.ACTIVE_BTN_BG,
            activeforeground=ModernStyle.BUTTON_FG,
            cursor="hand2"
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(bg=ModernStyle.ACTIVE_BTN_BG)

    def on_leave(self, e):
        self.config(bg=ModernStyle.BUTTON_BG)

class RequestBox(tk.Frame):
    def __init__(self, parent, index, **kwargs):
        super().__init__(parent, **kwargs)
        self.index = index
        self.show_response = False
        
        # Configure box styling
        self.config(
            bg=ModernStyle.BOX_BG,
            highlightbackground=ModernStyle.BORDER_COLOR,
            highlightthickness=1,
            padx=10,
            pady=10
        )
        
        # Header section with dark background
        header = tk.Frame(self, bg=ModernStyle.HEADER_BG, padx=10, pady=5)
        header.pack(fill=tk.X, pady=(0, 10))
        
        # EP number
        tk.Label(
            header,
            text=f"EP{self.index + 1}",
            font=(ModernStyle.FONT_FAMILY, 12, 'bold'),
            bg=ModernStyle.HEADER_BG,
            fg=ModernStyle.HEADER_FG
        ).pack(side=tk.LEFT)
        
        # Toggle buttons
        btn_frame = tk.Frame(header, bg=ModernStyle.HEADER_BG)
        btn_frame.pack(side=tk.RIGHT)
        
        self.req_btn = ModernButton(
            btn_frame,
            text="Request",
            command=lambda: self.toggle_view(False)
        )
        self.req_btn.pack(side=tk.LEFT, padx=2)
        
        self.resp_btn = ModernButton(
            btn_frame,
            text="Response",
            command=lambda: self.toggle_view(True)
        )
        self.resp_btn.pack(side=tk.LEFT, padx=2)
        
        # URL section
        url_frame = tk.Frame(self, bg=ModernStyle.BOX_BG)
        url_frame.pack(fill=tk.X, pady=5)
        
        self.url_var = tk.StringVar(value="URL: ")
        tk.Label(
            url_frame,
            textvariable=self.url_var,
            font=(ModernStyle.FONT_FAMILY, 10),
            wraplength=250,
            bg=ModernStyle.BOX_BG,
            fg=ModernStyle.TEXT_COLOR
        ).pack(fill=tk.X)
        
        # Content area with custom styling
        content_frame = tk.Frame(self, bg=ModernStyle.BOX_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.content = tk.Text(
            content_frame,
            height=8,
            width=40,
            wrap=tk.WORD,
            font=(ModernStyle.FONT_FAMILY, 9),
            bg=ModernStyle.BOX_BG,
            fg=ModernStyle.TEXT_COLOR,
            relief="flat",
            padx=5,
            pady=5
        )
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(content_frame, orient=tk.VERTICAL)
        scrollbar.config(command=self.content.yview)
        self.content.config(yscrollcommand=scrollbar.set)
        
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Referrer section with subtle background
        ref_frame = tk.Frame(self, bg=ModernStyle.BORDER_COLOR, padx=5, pady=5)
        ref_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.ref_var = tk.StringVar(value="Referrer: ")
        tk.Label(
            ref_frame,
            textvariable=self.ref_var,
            font=(ModernStyle.FONT_FAMILY, 9),
            wraplength=200,
            bg=ModernStyle.BORDER_COLOR,
            fg=ModernStyle.TEXT_COLOR
        ).pack(side=tk.LEFT)
        
        self.count_var = tk.StringVar(value="Count: 0")
        tk.Label(
            ref_frame,
            textvariable=self.count_var,
            font=(ModernStyle.FONT_FAMILY, 9, 'bold'),
            bg=ModernStyle.BORDER_COLOR,
            fg=ModernStyle.TEXT_COLOR
        ).pack(side=tk.RIGHT)

    def toggle_view(self, show_response):
        self.show_response = show_response
        self.update_content()
        # Update button states
        if show_response:
            self.resp_btn.config(bg=ModernStyle.ACTIVE_BTN_BG)
            self.req_btn.config(bg=ModernStyle.BUTTON_BG)
        else:
            self.req_btn.config(bg=ModernStyle.ACTIVE_BTN_BG)
            self.resp_btn.config(bg=ModernStyle.BUTTON_BG)

    def set_data(self, request_content, response_content, url, referrer, ref_count):
        self.request_content = request_content
        self.response_content = response_content
        self.url_var.set(f"URL: {url}")
        self.ref_var.set(f"Referrer: {referrer}")
        self.count_var.set(f"Count: {ref_count}")
        self.update_content()

    def update_content(self):
        self.content.delete('1.0', tk.END)
        if self.show_response:
            self.content.insert('1.0', self.response_content)
        else:
            self.content.insert('1.0', self.request_content)

class GridViewer(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg=ModernStyle.BG_COLOR)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = tk.Frame(self, bg=ModernStyle.BG_COLOR, pady=10)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ModernButton(
            header_frame,
            text="Open Directory",
            command=self.browse_directory
        ).pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Please select a directory")
        tk.Label(
            header_frame,
            textvariable=self.status_var,
            font=(ModernStyle.FONT_FAMILY, 10),
            bg=ModernStyle.BG_COLOR,
            fg=ModernStyle.TEXT_COLOR
        ).pack(side=tk.LEFT, padx=20)
        
        # Create canvas with custom scrollbar
        self.canvas = tk.Canvas(
            self,
            bg=ModernStyle.BG_COLOR,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrolling
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        # Grid frame
        self.grid_frame = tk.Frame(self.canvas, bg=ModernStyle.BG_COLOR)
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.grid_frame,
            anchor='nw'
        )
        
        # Configure grid weights
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        
        # Bind events
        self.grid_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select directory")
        if directory:
            self.load_directory(directory)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def load_directory(self, directory):
        try:
            dir_path = Path(directory)
            
            # Clear existing grid
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            
            # Load and process files (same as before)
            req_files = sorted(dir_path.glob("requests/Req*.txt"),
                             key=lambda x: int(re.findall(r'\d+', x.name)[0]))
            resp_files = sorted(dir_path.glob("responses/Resp*.txt"),
                              key=lambda x: int(re.findall(r'\d+', x.name)[0]))
            ref_files = sorted(dir_path.glob("referrers/Ref*.txt"),
                             key=lambda x: int(re.findall(r'\d+', x.name)[0]))
            
            # Calculate referrer counts
            referrer_counts = {}
            for ref_file in ref_files:
                with open(ref_file, 'r') as f:
                    referrer = f.read().strip()
                    referrer_counts[referrer] = referrer_counts.get(referrer, 0) + 1
            
            # Create grid
            for i, (req_file, resp_file, ref_file) in enumerate(zip(req_files, resp_files, ref_files)):
                # Read files
                with open(req_file, 'r') as f:
                    request_content = f.read()
                with open(resp_file, 'r') as f:
                    response_content = f.read()
                with open(ref_file, 'r') as f:
                    referrer = f.read().strip()
                
                # Extract URL
                url = request_content.split('\n')[0].split(' ')[1] if ' ' in request_content.split('\n')[0] else "Unknown"
                
                # Create and place box
                row = i // 2
                col = i % 2
                box = RequestBox(self.grid_frame, i)
                box.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                box.set_data(request_content, response_content, url, referrer, referrer_counts[referrer])
            
            self.status_var.set(f"Loaded {len(req_files)} items")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load directory: {str(e)}")
            self.status_var.set("Error loading directory")

def main():
    root = tk.Tk()
    root.title("Modern Request/Response Viewer")
    root.geometry("1400x900")
    root.configure(bg=ModernStyle.BG_COLOR)
    
    app = GridViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()