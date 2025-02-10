import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import win32gui
import win32ui
import win32con
import win32api
import keyboard
import json
import os

class CombinedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot and Mission Editor")
        self.root.geometry("1600x900")
        self.x = 0
        self.y = 0
        # Initialize state
        self.steps = []
        self.screenshot_counter = 1
        self.save_path = ""
        self.references = []
        self.dragged_item = None
        self.current_image = None
        
        # Create main interface
        self.create_main_interface()
        
        # Setup keyboard shortcut
        keyboard.on_press_key('shift', self.on_shift_press, suppress=False)
        
    def create_main_interface(self):
        # Main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Screenshot panel (left)
        self.screenshot_frame = self.create_screenshot_panel()
        
        # Mission editor panel (right)
        self.editor_frame = self.create_mission_editor()
        
        self.main_paned.add(self.screenshot_frame, weight=1)
        self.main_paned.add(self.editor_frame, weight=2)
        
        # Menu
        self.create_menu()
        
    def create_screenshot_panel(self):
        frame = ttk.LabelFrame(self.main_paned, text="Screenshot Tool")
        
        # Screenshot controls
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls, text="Set Save Path", 
                  command=self.set_save_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Take Screenshot", 
                  command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        
        self.path_label = ttk.Label(controls, text="No save path set", wraplength=200)
        self.path_label.pack(side=tk.LEFT, padx=5)

        # Create separate transparent window for viewfinder
        self.viewfinder_window = tk.Toplevel(self.root)
        self.viewfinder_window.attributes('-alpha', 0.3, '-topmost', True)
        self.viewfinder_window.overrideredirect(True)
        self.viewfinder_window.geometry("800x600")
        
        # Create viewfinder in the transparent window
        self.viewfinder = self.create_viewfinder(self.viewfinder_window)
        self.viewfinder.pack(fill=tk.BOTH, expand=True)
        
        return frame
        
    def create_viewfinder(self, parent):
        frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=2)
        frame.configure(width=800, height=600)
        frame.pack_propagate(False)

        # Create viewfinder elements
        bracket_length = 30
        bracket_thickness = 4
        bracket_color = '#00FF00'
        
        # Vertical edges
        left_edge = tk.Frame(frame, bg=bracket_color, width=bracket_thickness, height=9999)
        left_edge.place(x=0, y=0)
        
        right_edge = tk.Frame(frame, bg=bracket_color, width=bracket_thickness, height=9999)
        right_edge.place(relx=1.0, y=0, anchor='ne')
        
        # Horizontal edges
        top_edge = tk.Frame(frame, bg=bracket_color, width=9999, height=bracket_thickness)
        top_edge.place(x=0, y=0)
        
        bottom_edge = tk.Frame(frame, bg=bracket_color, width=9999, height=bracket_thickness)
        bottom_edge.place(x=0, rely=1.0, anchor='sw')
        
        # Corner brackets
        corners = [(0, 0, 'nw'), (1, 0, 'ne'), (0, 1, 'sw'), (1, 1, 'se')]
        for relx, rely, anchor in corners:
            h_corner = tk.Frame(frame, bg=bracket_color, width=bracket_length, height=bracket_thickness+2)
            h_corner.place(relx=relx, rely=rely, anchor=anchor)
            
            v_corner = tk.Frame(frame, bg=bracket_color, width=bracket_thickness+2, height=bracket_length)
            v_corner.place(relx=relx, rely=rely, anchor=anchor)
        
        # Center crosshair
        crosshair_size = 15
        crosshair_thickness = 2
        v_crosshair = tk.Frame(frame, bg=bracket_color, width=crosshair_thickness, height=crosshair_size*2)
        v_crosshair.place(relx=0.5, rely=0.5, anchor='center')
        
        h_crosshair = tk.Frame(frame, bg=bracket_color, width=crosshair_size*2, height=crosshair_thickness)
        h_crosshair.place(relx=0.5, rely=0.5, anchor='center')

        # Make window draggable
        frame.bind('<Button-1>', self.start_move)
        frame.bind('<B1-Motion>', self.do_move)
        
        return frame
        
    def create_mission_editor(self):
        frame = ttk.LabelFrame(self.main_paned, text="Mission Editor")
        
        # Sub-paned window
        editor_paned = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        editor_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Steps list
        steps_frame = ttk.LabelFrame(editor_paned, text="Steps")
        self.steps_list = tk.Listbox(steps_frame, selectmode=tk.SINGLE)
        self.steps_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.steps_list.bind("<ButtonRelease-1>", self.on_step_drop)
        
        # References and preview
        right_pane = ttk.PanedWindow(editor_paned, orient=tk.VERTICAL)
        
        # References list
        ref_frame = ttk.LabelFrame(right_pane, text="References")
        self.ref_list = tk.Listbox(ref_frame, selectmode=tk.SINGLE)
        self.ref_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ref_list.bind("<B1-Motion>", self.start_drag)
        self.ref_list.bind("<ButtonPress-1>", self.select_reference)
        self.ref_list.bind("<<ListboxSelect>>", self.show_image_preview)
        
        # Preview
        preview_frame = ttk.LabelFrame(right_pane, text="Preview")
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add to paned windows
        right_pane.add(ref_frame, weight=1)
        right_pane.add(preview_frame, weight=1)
        editor_paned.add(steps_frame, weight=1)
        editor_paned.add(right_pane, weight=2)
        
        return frame
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Steps", command=self.load_steps)
        file_menu.add_command(label="Save Mission", command=self.save_mission)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)
    
    def select_reference(self, event):
        index = self.ref_list.nearest(event.y)
        if index >= 0:
            self.dragged_item = self.references[index]
            
    def start_drag(self, event):
        self.root.config(cursor="hand2")
        
    def on_step_drop(self, event):
        self.root.config(cursor="")
        if self.dragged_item:
            target_index = self.steps_list.nearest(event.y)
            if target_index >= 0 and target_index < len(self.steps):
                if self.dragged_item not in self.steps[target_index]['references']:
                    self.steps[target_index]['references'].append(self.dragged_item)
                    self.update_steps_list()
                    self.highlight_step(target_index)
                self.dragged_item = None
                
    def highlight_step(self, index):
        self.steps_list.selection_clear(0, tk.END)
        self.steps_list.selection_set(index)
        self.root.after(1000, lambda: self.steps_list.selection_clear(index))
    
    def show_image_preview(self, event):
        index = self.ref_list.curselection()
        if index:
            ref_path = self.references[index[0]]
            try:
                img = Image.open(ref_path)
                max_width = self.preview_label.winfo_width() - 20
                max_height = self.preview_label.winfo_height() - 20
                img.thumbnail((max_width, max_height))
                self.current_image = ImageTk.PhotoImage(img)
                self.preview_label.configure(image=self.current_image)
            except Exception as e:
                self.preview_label.configure(
                    image=None,
                    text=f"Error loading image:\n{str(e)}"
                )
    
    def set_save_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path = path
            self.path_label.config(text=f"Save path: {path}")
            self.load_existing_references()
    
    def take_screenshot(self):
        if not self.save_path:
            messagebox.showerror("Error", "Please set a save path first!")
            return
            
        self.viewfinder_window.withdraw()
        self.root.withdraw()
        try:
            hwnd = win32gui.GetDesktopWindow()
            x = self.viewfinder_window.winfo_x()
            y = self.viewfinder_window.winfo_y()
            width = self.viewfinder_window.winfo_width()
            height = self.viewfinder_window.winfo_height()
            
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
                
            filename = f"sc{self.screenshot_counter}reference{self.screenshot_counter}.png"
            filepath = os.path.join(self.save_path, filename)
            im.save(filepath)
            
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            self.screenshot_counter += 1
            self.references.append(filepath)
            self.update_ref_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Screenshot failed: {str(e)}")
        finally:
            self.root.deiconify()
            self.viewfinder_window.deiconify()
    
    def on_shift_press(self, event):
        if event.name == 'shift' and event.event_type == 'down':
            self.take_screenshot()
    
    def load_steps(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.steps = self.parse_steps(file_path)
            self.update_steps_list()
    
    def parse_steps(self, file_path):
        steps = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line and line[0].isdigit():
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        steps.append({
                            'number': parts[0].strip(),
                            'action': parts[1].strip(),
                            'references': []
                        })
        return steps
    
    def load_existing_references(self):
        self.references = [os.path.join(self.save_path, f) for f in os.listdir(self.save_path)
                         if f.startswith('sc') and f.endswith('.png')]
        self.references.sort(key=lambda x: int(''.join(filter(str.isdigit, 
                           os.path.basename(x).split('reference')[0]))))
        self.update_ref_list()
    
    def update_steps_list(self):
        self.steps_list.delete(0, tk.END)
        for step in self.steps:
            ref_count = len(step['references'])
            display_text = f"Step {step['number']}: {step['action']}"
            display_text += f" ({ref_count} ref{'s' if ref_count != 1 else ''})"
            self.steps_list.insert(tk.END, display_text)
    
    def update_ref_list(self):
        self.ref_list.delete(0, tk.END)
        for ref in self.references:
            self.ref_list.insert(tk.END, os.path.basename(ref))
    
    def save_mission(self):
        mission_data = []
        for step in self.steps:
            mission_data.append({
                "Step": int(step['number']),
                "Action": step['action'],
                "ReferenceImages": step['references'],
                "ImageTitle": f"Step {step['number']} Reference Images",
                "ImageDescription": f"Step {step['number']} References"
            })
        
        with open('MissionBank.json', 'w') as f:
            json.dump(mission_data, f, indent=2)
        messagebox.showinfo("Success", "Mission saved to MissionBank.json")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.viewfinder_window.winfo_x() + deltax
        y = self.viewfinder_window.winfo_y() + deltay
        self.viewfinder_window.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CombinedApp()
    app.run()
