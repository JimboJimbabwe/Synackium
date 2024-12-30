import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import re
import math

class ModernStyle:
    BG_MAIN = "#f0f0f0"
    BOX_BG = "#ffffff"
    BOX_BORDER = "#2563eb"
    SELECTED_BORDER = "#1e40af"
    ARROW_COLOR = "#64748b"
    TEXT_COLOR = "#1e293b"
    HEADER_BG = "#1e293b"
    HEADER_FG = "#ffffff"

class DraggableBox:
    def __init__(self, canvas, x, y, width=200, height=150, title="", request="", response="", referrer=""):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.request = request
        self.response = response
        self.referrer = referrer
        self.show_response = False
        
        self.create_box()
        self.selected = False
        self.start_x = 0
        self.start_y = 0
        
    def create_box(self):
        # Create main box
        self.box = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            fill=ModernStyle.BOX_BG,
            outline=ModernStyle.BOX_BORDER,
            width=2,
            tags=("box",)
        )
        
        # Header background
        self.header = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + 30,
            fill=ModernStyle.HEADER_BG,
            outline=ModernStyle.HEADER_BG,
            tags=("box",)
        )
        
        # Title
        self.title_text = self.canvas.create_text(
            self.x + 10, self.y + 15,
            text=self.title,
            anchor="w",
            fill=ModernStyle.HEADER_FG,
            font=("Helvetica", 10, "bold"),
            tags=("box",)
        )
        
        # Toggle button (simulated with text)
        self.toggle = self.canvas.create_text(
            self.x + self.width - 10, self.y + 15,
            text="Req",
            anchor="e",
            fill=ModernStyle.HEADER_FG,
            font=("Helvetica", 9),
            tags=("box", "toggle")
        )
        
        # Content
        self.content = self.canvas.create_text(
            self.x + 10, self.y + 50,
            text=self.request[:100] + "..." if len(self.request) > 100 else self.request,
            anchor="nw",
            fill=ModernStyle.TEXT_COLOR,
            width=self.width - 20,
            font=("Helvetica", 9),
            tags=("box",)
        )
        
        # Referrer
        self.ref_box = self.canvas.create_rectangle(
            self.x + 5, self.y + self.height - 30,
            self.x + self.width - 5, self.y + self.height - 5,
            fill="#f8fafc",
            outline="#e2e8f0",
            tags=("box",)
        )
        
        self.ref_text = self.canvas.create_text(
            self.x + 10, self.y + self.height - 20,
            text=f"Ref: {self.referrer[:30]}..." if len(self.referrer) > 30 else f"Ref: {self.referrer}",
            anchor="w",
            fill=ModernStyle.TEXT_COLOR,
            font=("Helvetica", 8),
            tags=("box",)
        )
        
        # Bind events
        for item in [self.box, self.header, self.title_text, self.content, self.ref_box, self.ref_text]:
            self.canvas.tag_bind(item, "<Button-1>", self.on_press)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_release)
        
        # Bind toggle button
        self.canvas.tag_bind(self.toggle, "<Button-1>", self.toggle_content)
        
    def toggle_content(self, event):
        self.show_response = not self.show_response
        if self.show_response:
            self.canvas.itemconfig(self.toggle, text="Resp")
            content = self.response
        else:
            self.canvas.itemconfig(self.toggle, text="Req")
            content = self.request
            
        # Update content
        self.canvas.itemconfig(
            self.content,
            text=content[:100] + "..." if len(content) > 100 else content
        )
        
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.select()
        
    def on_drag(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        
        # Move all components
        for item in [self.box, self.header, self.title_text, self.toggle,
                    self.content, self.ref_box, self.ref_text]:
            self.canvas.move(item, dx, dy)
            
        self.start_x = event.x
        self.start_y = event.y
        self.x += dx
        self.y += dy
        
        # Update arrows
        self.canvas.event_generate("<<BoxMoved>>")
        
    def on_release(self, event):
        pass
        
    def select(self):
        if not self.selected:
            self.canvas.itemconfig(self.box, outline=ModernStyle.SELECTED_BORDER, width=3)
            self.selected = True
            
    def deselect(self):
        if self.selected:
            self.canvas.itemconfig(self.box, outline=ModernStyle.BOX_BORDER, width=2)
            self.selected = False

class FlowViewer(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create canvas
        self.canvas = tk.Canvas(
            self,
            bg=ModernStyle.BG_MAIN,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.add_scrollbars()
        
        # Store boxes
        self.boxes = []
        
        # Bind events
        self.canvas.bind("<<BoxMoved>>", self.update_arrows)
        self.canvas.bind("<Button-1>", self.deselect_all)
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Open Directory", command=self.load_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Arrange Horizontally", command=self.arrange_horizontal).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Arrange Vertically", command=self.arrange_vertical).pack(side=tk.LEFT, padx=5)
        
    def add_scrollbars(self):
        # Create scrollbars
        x_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        y_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        
        # Configure canvas
        self.canvas.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        
        # Pack scrollbars
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def load_directory(self):
        directory = filedialog.askdirectory(title="Select directory")
        if directory:
            try:
                dir_path = Path(directory)
                
                # Clear existing boxes
                self.canvas.delete("all")
                self.boxes.clear()
                
                # Load files
                req_files = sorted(dir_path.glob("requests/Req*.txt"),
                                 key=lambda x: int(re.findall(r'\d+', x.name)[0]))
                resp_files = sorted(dir_path.glob("responses/Resp*.txt"),
                                 key=lambda x: int(re.findall(r'\d+', x.name)[0]))
                ref_files = sorted(dir_path.glob("referrers/Ref*.txt"),
                                 key=lambda x: int(re.findall(r'\d+', x.name)[0]))
                
                # Create boxes
                for i, (req_file, resp_file, ref_file) in enumerate(zip(req_files, resp_files, ref_files)):
                    with open(req_file, 'r') as f:
                        request = f.read()
                    with open(resp_file, 'r') as f:
                        response = f.read()
                    with open(ref_file, 'r') as f:
                        referrer = f.read().strip()
                        
                    # Create box
                    box = DraggableBox(
                        self.canvas,
                        x=50 + (i % 3) * 250,
                        y=50 + (i // 3) * 200,
                        title=f"EP{i+1}",
                        request=request,
                        response=response,
                        referrer=referrer
                    )
                    self.boxes.append(box)
                
                # Draw arrows
                self.draw_arrows()
                
                # Configure scroll region
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load directory: {str(e)}")
                
    def draw_arrows(self):
        for i in range(len(self.boxes) - 1):
            self.draw_arrow(self.boxes[i], self.boxes[i + 1])
            
    def draw_arrow(self, box1, box2):
        # Calculate arrow points
        start_x = box1.x + box1.width
        start_y = box1.y + box1.height // 2
        end_x = box2.x
        end_y = box2.y + box2.height // 2
        
        # Draw arrow line
        self.canvas.create_line(
            start_x, start_y,
            end_x, end_y,
            fill=ModernStyle.ARROW_COLOR,
            width=2,
            arrow=tk.LAST,
            smooth=True,
            tags=("arrow",)
        )
        
    def update_arrows(self, event=None):
        self.canvas.delete("arrow")
        self.draw_arrows()
        
    def deselect_all(self, event):
        # Only deselect if clicked on canvas background
        if event.widget == self.canvas and not self.canvas.find_withtag("current"):
            for box in self.boxes:
                box.deselect()
                
    def arrange_horizontal(self):
        spacing = 250
        for i, box in enumerate(self.boxes):
            x = 50 + i * spacing
            y = 50
            dx = x - box.x
            dy = y - box.y
            self.canvas.move("box", dx, dy)
            box.x = x
            box.y = y
        self.update_arrows()
        
    def arrange_vertical(self):
        spacing = 200
        for i, box in enumerate(self.boxes):
            x = 50
            y = 50 + i * spacing
            dx = x - box.x
            dy = y - box.y
            self.canvas.move("box", dx, dy)
            box.x = x
            box.y = y
        self.update_arrows()

def main():
    root = tk.Tk()
    root.title("Flow Diagram Viewer")
    root.geometry("1200x800")
    app = FlowViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
