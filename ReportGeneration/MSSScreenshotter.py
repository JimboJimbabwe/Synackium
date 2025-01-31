import tkinter as tk
from tkinter import filedialog, messagebox
from mss import mss
from PIL import Image
import os
import numpy as np

class ScreenshotWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Widget")
        self.root.attributes('-alpha', 0.7)  # Make window semi-transparent
        
        # Initialize screenshot counter and save path
        self.screenshot_counter = 1
        self.save_path = ""
        
        # Initialize mss
        self.sct = mss()
        
        # Create main frame
        self.frame = tk.Frame(self.root, bg='gray')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create viewfinder (transparent area) - now larger with smaller margins
        self.viewfinder = tk.Frame(self.frame, bg='white')
        self.viewfinder.place(relx=0.05, rely=0.05, relwidth=0.95, relheight=0.95)
        
        # Create resize handles
        self.create_resize_handles()
        
        # Create control buttons
        self.create_buttons()
        
        # Bind mouse events for moving the window
        self.frame.bind('<Button-1>', self.start_move)
        self.frame.bind('<B1-Motion>', self.do_move)
        
        # Set minimum size - increased for better usability
        self.root.minsize(250, 250)
        
        # Variables for window movement
        self.x = 0
        self.y = 0

    def create_resize_handles(self):
        # Made resize handles smaller to not intrude on larger viewfinder
        handle_size = 8
        corners = ['se', 'sw', 'ne', 'nw']
        for corner in corners:
            handle = tk.Frame(self.frame, bg='black', width=handle_size, height=handle_size)
            if 's' in corner:
                rely = 1.0
            else:
                rely = 0.0
            if 'e' in corner:
                relx = 1.0
            else:
                relx = 0.0
            handle.place(relx=relx, rely=rely, anchor=corner)
            handle.bind('<Button-1>', lambda e, c=corner: self.start_resize(e, c))
            handle.bind('<B1-Motion>', self.do_resize)

    def create_buttons(self):
        button_frame = tk.Frame(self.frame)
        button_frame.pack(side=tk.BOTTOM, pady=3)  # Reduced padding to give more space to viewfinder
        
        tk.Button(button_frame, text="Set Save Path", 
                 command=self.set_save_path).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Take Screenshot", 
                 command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Exit", 
                 command=self.graceful_exit,
                 bg='red', fg='white').pack(side=tk.LEFT, padx=5)

    def generate_file_lists(self):
        if not self.save_path:
            return
            
        # Get all PNG files that match our naming convention
        files = [f for f in os.listdir(self.save_path) 
                if f.startswith('sc') and f.endswith('.png')]
        
        # Sort files to ensure correct order
        files.sort(key=lambda x: int(''.join(filter(str.isdigit, x.split('reference')[0]))))
        
        # Generate the two lists
        simple_list_path = os.path.join(self.save_path, 'screenshot_list.txt')
        reference_list_path = os.path.join(self.save_path, 'reference_list.txt')
        
        # Write simple list
        with open(simple_list_path, 'w') as f:
            for filename in files:
                f.write(f"{filename}\n")
                
        # Write reference list
        with open(reference_list_path, 'w') as f:
            for filename in files:
                f.write(f"Reference: {filename}\n")
                
        return simple_list_path, reference_list_path

    def graceful_exit(self):
        try:
            if self.save_path:
                simple_list, reference_list = self.generate_file_lists()
                messagebox.showinfo("Success", 
                    f"File lists have been created:\n"
                    f"1. {os.path.basename(simple_list)}\n"
                    f"2. {os.path.basename(reference_list)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate lists: {str(e)}")
        finally:
            self.sct.close()  # Clean up mss
            self.root.quit()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event, corner):
        self.resize_corner = corner
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()

    def do_resize(self, event):
        delta_x = event.x_root - self.start_x
        delta_y = event.y_root - self.start_y
        
        new_width = self.start_width
        new_height = self.start_height
        new_x = self.root.winfo_x()
        new_y = self.root.winfo_y()
        
        if 'e' in self.resize_corner:
            new_width += delta_x
        elif 'w' in self.resize_corner:
            new_width -= delta_x
            new_x += delta_x
            
        if 's' in self.resize_corner:
            new_height += delta_y
        elif 'n' in self.resize_corner:
            new_height -= delta_y
            new_y += delta_y
            
        # Enforce minimum size
        new_width = max(250, new_width)  # Increased minimum width
        new_height = max(250, new_height)  # Increased minimum height
        
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

    def set_save_path(self):
        self.save_path = filedialog.askdirectory()
        if not self.save_path:
            self.save_path = ""

    def take_screenshot(self):
        if not self.save_path:
            messagebox.showerror("Error", "Please set a save path first!")
            return
            
        # Get viewfinder coordinates relative to screen
        x = self.root.winfo_x() + self.viewfinder.winfo_x()
        y = self.root.winfo_y() + self.viewfinder.winfo_y()
        width = self.viewfinder.winfo_width()
        height = self.viewfinder.winfo_height()

        # Hide window temporarily
        self.root.withdraw()
        self.root.update()
        
        try:
            # Take screenshot using mss
            monitor = {"top": y, "left": x, "width": width, "height": height}
            screenshot = self.sct.grab(monitor)
            
            # Convert to PIL Image
            image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            # Generate filename
            filename = f"sc{self.screenshot_counter}reference{self.screenshot_counter}.png"
            filepath = os.path.join(self.save_path, filename)
            
            # Save screenshot
            image.save(filepath)
            
            # Increment counter
            self.screenshot_counter += 1
            
        except Exception as e:
            messagebox.showerror("Error", f"Screenshot failed: {str(e)}")
            
        finally:
            # Show window again
            self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotWidget()
    app.run()
