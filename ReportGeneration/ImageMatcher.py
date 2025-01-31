import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class MissionEditor:
    def __init__(self, root):
        self.root = root
        self.steps = []
        self.references = []
        self.dragged_item = None
        self.current_image = None  # To prevent garbage collection
        self.setup_gui()
        
    def setup_gui(self):
        self.root.title("Mission Editor")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f0f0")

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Listbox", background="#ffffff", selectbackground="#e0e0e0")
        style.configure("TFrame", background="#ffffff")

        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane (Steps)
        self.left_pane = ttk.Frame(self.main_paned, width=500)
        self.steps_list = tk.Listbox(self.left_pane, selectmode=tk.SINGLE, 
                                   bg="white", font=('Arial', 11), relief=tk.FLAT)
        self.steps_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.steps_list.bind("<ButtonRelease-1>", self.on_step_drop)
        
        # Right pane (References + Preview)
        self.right_pane = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        
        # References list
        self.ref_frame = ttk.Frame(self.right_pane)
        self.ref_list = tk.Listbox(self.ref_frame, selectmode=tk.SINGLE, 
                                 bg="white", font=('Arial', 11), relief=tk.FLAT)
        self.ref_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ref_list.bind("<B1-Motion>", self.start_drag)
        self.ref_list.bind("<ButtonPress-1>", self.select_reference)
        self.ref_list.bind("<<ListboxSelect>>", self.show_image_preview)
        
        # Image preview panel
        self.preview_frame = ttk.Frame(self.right_pane, relief=tk.SUNKEN, borderwidth=2)
        self.preview_label = ttk.Label(self.preview_frame, background="#ffffff")
        self.preview_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.right_pane.add(self.ref_frame, weight=2)
        self.right_pane.add(self.preview_frame, weight=1)
        
        self.main_paned.add(self.left_pane, weight=1)
        self.main_paned.add(self.right_pane, weight=2)

        # Menu
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Load Steps", command=self.load_steps)
        self.file_menu.add_command(label="Load References", command=self.load_references)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save Mission", command=self.save_mission)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

    def load_steps(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.steps = self.parse_steps(file_path)
            self.update_steps_list()
            self.generate_mission_json()
            
    def parse_steps(self, file_path):
        steps = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            start_index = next((i for i, line in enumerate(lines) 
                              if "##### Steps Taken:" in line), -1) + 1
            if start_index > 0:
                for line in lines[start_index:]:
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

    def load_references(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.references = self.parse_references(file_path)
            self.update_ref_list()

    def parse_references(self, file_path):
        references = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith("Reference:"):
                    ref_path = line.split(": ")[1].strip()
                    if os.path.exists(ref_path):
                        references.append(ref_path)
                    else:
                        messagebox.showwarning("Missing File", 
                                            f"Reference file not found: {ref_path}")
        return references

    def update_steps_list(self):
        self.steps_list.delete(0, tk.END)
        for step in self.steps:
            ref_count = len(step['references'])
            display_text = f"Step {step['number']}: {step['action']}"
            display_text += f" ({ref_count} reference{'s' if ref_count !=1 else ''})"
            self.steps_list.insert(tk.END, display_text)

    def update_ref_list(self):
        self.ref_list.delete(0, tk.END)
        for ref in self.references:
            self.ref_list.insert(tk.END, os.path.basename(ref))

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
                # Add reference if not already present
                if self.dragged_item not in self.steps[target_index]['references']:
                    self.steps[target_index]['references'].append(self.dragged_item)
                    self.generate_mission_json()
                    self.update_steps_list()
                    self.highlight_step(target_index)
                self.dragged_item = None

    def show_image_preview(self, event):
        index = self.ref_list.curselection()
        if index:
            ref_path = self.references[index[0]]
            try:
                img = Image.open(ref_path)
                # Calculate maximum size while maintaining aspect ratio
                max_width = self.preview_frame.winfo_width() - 20
                max_height = self.preview_frame.winfo_height() - 20
                
                img.thumbnail((max_width, max_height))
                self.current_image = ImageTk.PhotoImage(img)
                self.preview_label.configure(image=self.current_image, text="")
            except Exception as e:
                self.preview_label.configure(
                    image=None,
                    text=f"Error loading image:\n{str(e)}",
                    foreground="red"
                )

    def highlight_step(self, index):
        self.steps_list.selection_clear(0, tk.END)
        self.steps_list.selection_set(index)
        self.root.after(1000, lambda: self.steps_list.selection_clear(index))

    def generate_mission_json(self):
        mission_data = []
        for i, step in enumerate(self.steps):
            mission_data.append({
                "Step": int(step['number']),
                "Action": step['action'],
                "ReferenceImages": step['references'],
                "ImageTitle": f"Step {step['number']} Reference Images",
                "ImageDescription": f"Step {step['number']} References"
            })
        
        with open('MissionBank.json', 'w') as f:
            json.dump(mission_data, f, indent=2)

    def save_mission(self):
        self.generate_mission_json()
        messagebox.showinfo("Success", "Mission saved to MissionBank.json")

if __name__ == "__main__":
    root = tk.Tk()
    app = MissionEditor(root)
    root.mainloop()
