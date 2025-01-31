import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import win32gui
import win32ui
import win32con
import win32api
import os
import keyboard

class ViewfinderScreenshot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Tool")
        self.root.attributes('-alpha', 0.3, '-topmost', True)
        self.root.overrideredirect(True)
        
        # Set initial size to 800x800
        self.root.geometry("1800x800")
        
        self.screenshot_counter = 1
        self.save_path = ""
        self.viewfinder_elements = []  # Store references to viewfinder elements
        
        # Main frame with transparent background
        self.frame = tk.Frame(self.root)
        self.frame.configure(bg='')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create viewfinder elements
        self.create_viewfinder()
        
        # Create control panel
        self.create_control_panel()
        
        # Bind events
        self.frame.bind('<Button-1>', self.start_move)
        self.frame.bind('<B1-Motion>', self.do_move)
        
        # Setup keyboard shortcut
        keyboard.on_press_key('shift', self.on_shift_press, suppress=False)
        
        # Set minimum size
        self.root.minsize(1800, 800)
        self.x = 0
        self.y = 0

    def clear_viewfinder(self):
        """Remove all viewfinder elements"""
        for element in self.viewfinder_elements:
            element.destroy()
        self.viewfinder_elements = []

    def create_viewfinder(self):
        """Create a camera viewfinder-like interface"""
        self.clear_viewfinder()
        
        bracket_length = 30
        bracket_thickness = 4
        bracket_color = '#00FF00'
        
        # Create vertical edges
        left_edge = tk.Frame(self.frame, bg=bracket_color, width=bracket_thickness, height=9999)
        left_edge.place(x=0, y=0)
        self.viewfinder_elements.append(left_edge)
        
        right_edge = tk.Frame(self.frame, bg=bracket_color, width=bracket_thickness, height=9999)
        right_edge.place(relx=1.0, y=0, anchor='ne')
        self.viewfinder_elements.append(right_edge)
        
        # Create horizontal edges
        top_edge = tk.Frame(self.frame, bg=bracket_color, width=9999, height=bracket_thickness)
        top_edge.place(x=0, y=0)
        self.viewfinder_elements.append(top_edge)
        
        bottom_edge = tk.Frame(self.frame, bg=bracket_color, width=9999, height=bracket_thickness)
        bottom_edge.place(x=0, rely=1.0, anchor='sw')
        self.viewfinder_elements.append(bottom_edge)
        
        # Corner brackets
        corners = [
            (0, 0, 'nw'), (1, 0, 'ne'),
            (0, 1, 'sw'), (1, 1, 'se')
        ]
        
        for relx, rely, anchor in corners:
            # Horizontal part of corner
            h_corner = tk.Frame(self.frame, bg=bracket_color,
                              width=bracket_length, height=bracket_thickness+2)
            h_corner.place(relx=relx, rely=rely, anchor=anchor)
            self.viewfinder_elements.append(h_corner)
            
            # Vertical part of corner
            v_corner = tk.Frame(self.frame, bg=bracket_color,
                              width=bracket_thickness+2, height=bracket_length)
            v_corner.place(relx=relx, rely=rely, anchor=anchor)
            self.viewfinder_elements.append(v_corner)
        
        # Create center crosshair
        crosshair_size = 15
        crosshair_thickness = 2
        
        # Vertical line of crosshair
        v_crosshair = tk.Frame(self.frame, bg=bracket_color,
                              width=crosshair_thickness, height=crosshair_size*2)
        v_crosshair.place(relx=0.5, rely=0.5, anchor='center')
        self.viewfinder_elements.append(v_crosshair)
        
        # Horizontal line of crosshair
        h_crosshair = tk.Frame(self.frame, bg=bracket_color,
                              width=crosshair_size*2, height=crosshair_thickness)
        h_crosshair.place(relx=0.5, rely=0.5, anchor='center')
        self.viewfinder_elements.append(h_crosshair)
        
        # Create resize handles
        self.create_resize_handles(bracket_color)

    def create_resize_handles(self, handle_color):
        """Create small corner handles for resizing"""
        handle_size = 8
        corners = ['se', 'sw', 'ne', 'nw']
        
        for corner in corners:
            handle = tk.Frame(self.frame, bg=handle_color, 
                            width=handle_size, height=handle_size,
                            cursor='crosshair')
            
            if 's' in corner:
                rely = 1.0
            else:
                rely = 0.0
                
            if 'e' in corner:
                relx = 1.0
            else:
                relx = 0.0
                
            handle.place(relx=relx, rely=rely, anchor=corner)
            
            # Bind the events directly to the handle
            handle.bind('<Button-1>', lambda e, c=corner: self.start_resize(e, c))
            handle.bind('<B1-Motion>', lambda e, c=corner: self.do_resize(e, c))
            handle.bind('<ButtonRelease-1>', self.end_resize)
            
            self.viewfinder_elements.append(handle)

    def create_control_panel(self):
        """Create a separate window for controls"""
        self.control_panel = tk.Toplevel(self.root)
        self.control_panel.title("Screenshot Controls")
        self.control_panel.geometry("300x180")
        self.control_panel.resizable(False, False)
        
        # Style the control panel
        self.control_panel.configure(bg='#2c2c2c')
        style = {
            'bg': '#2c2c2c',
            'fg': '#ffffff',
            'font': ('Arial', 10)
        }
        
        # Info label
        tk.Label(self.control_panel, 
                text="Press Shift to capture\nDrag corners to resize",
                **style).pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(self.control_panel, bg='#2c2c2c')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        button_style = {
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 5,
            'font': ('Arial', 9)
        }
        
        tk.Button(button_frame, 
                 text="Set Save Path",
                 command=self.set_save_path,
                 bg='#4a90e2',
                 fg='white',
                 **button_style).pack(side=tk.LEFT, expand=True, padx=5)
        
        tk.Button(button_frame,
                 text="Take Screenshot",
                 command=self.take_screenshot,
                 bg='#2ecc71',
                 fg='white',
                 **button_style).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Exit button
        tk.Button(self.control_panel,
                 text="Exit",
                 command=self.graceful_exit,
                 bg='#e74c3c',
                 fg='white',
                 **button_style).pack(side=tk.BOTTOM, pady=10)
        
        # Save path label
        self.path_label = tk.Label(self.control_panel,
                                 text="No save path set",
                                 wraplength=280,
                                 **style)
        self.path_label.pack(pady=5)

    # Window movement methods
    def start_move(self, event):
        """Start window movement"""
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        """Move the window"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    # Window resize methods
    def start_resize(self, event, corner):
        """Start window resizing"""
        self.resize_corner = corner
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.start_width = self.root.winfo_width()
        self.start_height = self.root.winfo_height()
        self.start_rootx = self.root.winfo_x()
        self.start_rooty = self.root.winfo_y()

    def do_resize(self, event, corner):
        """Handle resize operation"""
        if not hasattr(self, 'start_x'):
            return
            
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y
        
        new_width = self.start_width
        new_height = self.start_height
        new_x = self.start_rootx
        new_y = self.start_rooty
        
        # Calculate new dimensions based on which corner is being dragged
        if corner == 'se':
            new_width = max(800, self.start_width + dx)
            new_height = max(1800, self.start_height + dy)
        elif corner == 'sw':
            new_width = max(800, self.start_width - dx)
            new_height = max(1800, self.start_height + dy)
            new_x = self.start_rootx + (self.start_width - new_width)
        elif corner == 'ne':
            new_width = max(800, self.start_width + dx)
            new_height = max(1800, self.start_height - dy)
            new_y = self.start_rooty + (self.start_height - new_height)
        elif corner == 'nw':
            new_width = max(800, self.start_width - dx)
            new_height = max(1800, self.start_height - dy)
            new_x = self.start_rootx + (self.start_width - new_width)
            new_y = self.start_rooty + (self.start_height - new_height)
        
        # Update the window geometry
        self.root.geometry(f'{new_width}x{new_height}+{new_x}+{new_y}')
        self.root.update_idletasks()
        self.create_viewfinder()

    def end_resize(self, event):
        """Clean up after resize operation"""
        if hasattr(self, 'start_x'):
            del self.start_x
            del self.start_y
            del self.start_width
            del self.start_height
            del self.start_rootx
            del self.start_rooty

    # Screenshot methods
    def on_shift_press(self, event):
        """Handle shift key press for taking screenshots"""
        if event.name == 'shift' and event.event_type == 'down':
            if self.save_path:
                self.take_screenshot()
            else:
                messagebox.showerror("Error", "Please set a save path first!")

    def capture_screen_area(self, x, y, width, height):
        """Capture the specified area of the screen"""
        hwnd = win32gui.GetDesktopWindow()
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (x, y), win32con.SRCCOPY)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        
        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        return im

    def take_screenshot(self):
        """Take a screenshot of the selected area"""
        if not self.save_path:
            messagebox.showerror("Error", "Please set a save path first!")
            return
        
        self.root.withdraw()
        self.control_panel.withdraw()
        self.root.update()
        
        try:
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            image = self.capture_screen_area(x, y, width, height)
            filename = f"sc{self.screenshot_counter}reference{self.screenshot_counter}.png"
            filepath = os.path.join(self.save_path, filename)
            image.save(filepath)
            self.screenshot_counter += 1
            
        except Exception as e:
            messagebox.showerror("Error", f"Screenshot failed: {str(e)}")
            
        finally:
            self.root.deiconify()
            self.control_panel.deiconify()

    def set_save_path(self):
        """Set the save path for screenshots"""
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.config(text=f"Save path: {path}")
        else:
            self.save_path = ""
            self.path_label.config(text="No save path set")

    def generate_file_lists(self):
        """Generate reference files lists"""
        if not self.save_path:
            return
        
        files = [f for f in os.listdir(self.save_path) 
                if f.startswith('sc') and f.endswith('.png')]
        files.sort(key=lambda x: int(''.join(filter(str.isdigit, x.split('reference')[0]))))
        
        simple_list_path = os.path.join(self.save_path, 'screenshot_list.txt')
        reference_list_path = os.path.join(self.save_path, 'reference_list.txt')
        
        with open(simple_list_path, 'w') as f:
            for filename in files:
                f.write(f"{filename}\n")
                
        with open(reference_list_path, 'w') as f:
            for filename in files:
                f.write(f"Reference: {filename}\n")
                
        return simple_list_path, reference_list_path

    def graceful_exit(self):
        """Clean up and exit the application"""
        try:
            keyboard.unhook_all()
            if self.save_path:
                simple_list, reference_list = self.generate_file_lists()
                messagebox.showinfo("Success", 
                    f"File lists have been created:\n"
                    f"1. {os.path.basename(simple_list)}\n"
                    f"2. {os.path.basename(reference_list)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate lists: {str(e)}")
        finally:
            self.root.quit()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ViewfinderScreenshot()
    app.run()
