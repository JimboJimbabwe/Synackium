import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import win32gui
import win32ui
import win32con
import win32api
import os
import keyboard

class ScreenshotWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Widget")
        self.root.attributes('-alpha', 0.7)
        
        self.screenshot_counter = 1
        self.save_path = ""
        
        self.frame = tk.Frame(self.root, bg='gray')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.viewfinder = tk.Frame(self.frame, bg='white')
        self.viewfinder.place(relx=0.05, rely=0.05, relwidth=0.95, relheight=0.95)
        
        self.create_resize_handles()
        self.create_buttons()
        
        self.frame.bind('<Button-1>', self.start_move)
        self.frame.bind('<B1-Motion>', self.do_move)
        
        keyboard.on_press_key('shift', self.on_shift_press, suppress=False)
        
        self.root.minsize(250, 250)
        self.x = 0
        self.y = 0

    def capture_screen_area(self, x, y, width, height):
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

    def on_shift_press(self, event):
        if event.name == 'shift' and event.event_type == 'down':
            if self.save_path:
                self.take_screenshot()
            else:
                messagebox.showerror("Error", "Please set a save path first!")

    def create_resize_handles(self):
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
        button_frame.pack(side=tk.BOTTOM, pady=3)
        
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
            
        new_width = max(250, new_width)
        new_height = max(250, new_height)
        
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

    def set_save_path(self):
        self.save_path = filedialog.askdirectory()
        if not self.save_path:
            self.save_path = ""

    def take_screenshot(self):
        if not self.save_path:
            messagebox.showerror("Error", "Please set a save path first!")
            return
            
        x = self.root.winfo_x() + self.viewfinder.winfo_x()
        y = self.root.winfo_y() + self.viewfinder.winfo_y()
        width = self.viewfinder.winfo_width()
        height = self.viewfinder.winfo_height()

        self.root.withdraw()
        self.root.update()
        
        try:
            image = self.capture_screen_area(x, y, width, height)
            filename = f"sc{self.screenshot_counter}reference{self.screenshot_counter}.png"
            filepath = os.path.join(self.save_path, filename)
            image.save(filepath)
            self.screenshot_counter += 1
            
        except Exception as e:
            messagebox.showerror("Error", f"Screenshot failed: {str(e)}")
            
        finally:
            self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenshotWidget()
    app.run()
