import customtkinter as ctk
import json
from tkinter import ttk, scrolledtext
import tkinter as tk
from ttkbootstrap import Style


class PentestChecklistGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Pentest Checklist Tool")
        self.root.geometry("1200x800")

        # Set the theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load JSON data
        self.load_json_data()

        # Create main layout
        self.create_layout()

    def load_json_data(self):
        """Load JSON data from files"""
        with open('IDORList.json', 'r') as f:
            self.idor_data = json.load(f)
        with open('SQLJson.json', 'r') as f:
            self.sql_data = json.load(f)

    def create_layout(self):
        """Create the main layout of the application"""
        # Create left sidebar for navigation
        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Create main content area
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Add title to sidebar
        ctk.CTkLabel(self.sidebar,
                     text="Navigation",
                     font=("Arial", 20, "bold")).pack(pady=10)

        # Add navigation buttons
        self.create_nav_buttons()

        # Create notebook for main content
        self.notebook = ttk.Notebook(self.main_content)
        self.notebook.pack(fill="both", expand=True)

        # Initialize content pages
        self.initialize_content_pages()

    def create_nav_buttons(self):
        """Create navigation buttons in sidebar"""
        buttons = [
            ("IDOR Overview", lambda: self.show_idor_overview()),
            ("SQL Injection Overview", lambda: self.show_sql_overview()),
            ("IDOR Details", lambda: self.show_idor_details()),
            ("SQL Injection Details", lambda: self.show_sql_details()),
            ("Methodology", lambda: self.show_methodology())
        ]

        for text, command in buttons:
            ctk.CTkButton(self.sidebar,
                          text=text,
                          command=command,
                          width=180).pack(pady=5)

    def initialize_content_pages(self):
        """Initialize all content pages"""
        # Create frames for different content
        self.idor_frame = ctk.CTkFrame(self.notebook)
        self.sql_frame = ctk.CTkFrame(self.notebook)
        self.idor_details_frame = ctk.CTkFrame(self.notebook)
        self.sql_details_frame = ctk.CTkFrame(self.notebook)
        self.methodology_frame = ctk.CTkFrame(self.notebook)

        # Add frames to notebook
        self.notebook.add(self.idor_frame, text="IDOR Overview")
        self.notebook.add(self.sql_frame, text="SQL Injection")
        self.notebook.add(self.idor_details_frame, text="IDOR Details")
        self.notebook.add(self.sql_details_frame, text="SQL Details")
        self.notebook.add(self.methodology_frame, text="Methodology")

    def create_scrollable_text(self, parent):
        """Create a scrollable text widget"""
        text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD,
                                                font=("Arial", 11),
                                                bg='#2b2b2b', fg='white')
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        return text_widget

    def show_idor_overview(self):
        """Display IDOR overview"""
        self.clear_frame(self.idor_frame)
        text_widget = self.create_scrollable_text(self.idor_frame)

        for category in self.idor_data["idor_testing_locations"]:
            text_widget.insert(tk.END, f"\n=== {category['category']} ===\n", "header")
            text_widget.insert(tk.END, f"{category['description']}\n\n")

            if "examples" in category:
                text_widget.insert(tk.END, "Examples:\n", "subheader")
                for example in category["examples"]:
                    text_widget.insert(tk.END, f"• {example['type']}: {example['example']}\n")
                    text_widget.insert(tk.END, f"  Note: {example['testing_notes']}\n")

        text_widget.configure(state='disabled')
        self.notebook.select(0)

    def show_sql_overview(self):
        """Display SQL injection overview"""
        self.clear_frame(self.sql_frame)
        text_widget = self.create_scrollable_text(self.sql_frame)

        for technique in self.sql_data["sql_injection_bypasses"]:
            text_widget.insert(tk.END, f"\n=== {technique['title']} ===\n", "header")
            text_widget.insert(tk.END, f"{technique['description']}\n\n")

            text_widget.insert(tk.END, "Examples:\n", "subheader")
            if isinstance(technique["example"], dict):
                for db, example in technique["example"].items():
                    text_widget.insert(tk.END, f"• {db}: {example}\n")
            elif isinstance(technique["example"], list):
                for example in technique["example"]:
                    text_widget.insert(tk.END, f"• {example}\n")
            else:
                text_widget.insert(tk.END, f"• {technique['example']}\n")

        text_widget.configure(state='disabled')
        self.notebook.select(1)

    def show_idor_details(self):
        """Display detailed IDOR information"""
        self.clear_frame(self.idor_details_frame)
        text_widget = self.create_scrollable_text(self.idor_details_frame)

        for category in self.idor_data["idor_testing_locations"]:
            text_widget.insert(tk.END, f"\n=== {category['category']} ===\n", "header")

            if "vulnerable_areas" in category:
                for area in category["vulnerable_areas"]:
                    text_widget.insert(tk.END, f"\nArea: {area['area']}\n", "subheader")
                    if "common_endpoints" in area:
                        text_widget.insert(tk.END, "Common Endpoints:\n")
                        for endpoint in area["common_endpoints"]:
                            text_widget.insert(tk.END, f"• {endpoint}\n")
                    if "testing_approach" in area:
                        text_widget.insert(tk.END, f"Testing Approach: {area['testing_approach']}\n")

        text_widget.configure(state='disabled')
        self.notebook.select(2)

    def show_sql_details(self):
        """Display detailed SQL injection information"""
        self.clear_frame(self.sql_details_frame)
        text_widget = self.create_scrollable_text(self.sql_details_frame)

        for technique in self.sql_data["sql_injection_bypasses"]:
            text_widget.insert(tk.END, f"\n=== {technique['title']} ===\n", "header")
            text_widget.insert(tk.END, f"Description: {technique['description']}\n\n")

            text_widget.insert(tk.END, "Example Usage:\n", "subheader")
            if isinstance(technique["example"], dict):
                for db, example in technique["example"].items():
                    text_widget.insert(tk.END, f"Database: {db}\n")
                    text_widget.insert(tk.END, f"Payload: {example}\n\n")
            elif isinstance(technique["example"], list):
                for example in technique["example"]:
                    text_widget.insert(tk.END, f"• {example}\n")
            else:
                text_widget.insert(tk.END, f"• {technique['example']}\n")

        text_widget.configure(state='disabled')
        self.notebook.select(3)

    def show_methodology(self):
        """Display testing methodology"""
        self.clear_frame(self.methodology_frame)
        text_widget = self.create_scrollable_text(self.methodology_frame)

        text_widget.insert(tk.END, "=== Testing Methodology ===\n\n", "header")

        text_widget.insert(tk.END, "Prerequisites:\n", "subheader")
        for prereq in self.idor_data["testing_methodology"]["prerequisites"]:
            text_widget.insert(tk.END, f"• {prereq}\n")

        text_widget.insert(tk.END, "\nTesting Steps:\n", "subheader")
        for step in self.idor_data["testing_methodology"]["testing_steps"]:
            text_widget.insert(tk.END, f"• {step}\n")

        text_widget.configure(state='disabled')
        self.notebook.select(4)

    def clear_frame(self, frame):
        """Clear all widgets from a frame"""
        for widget in frame.winfo_children():
            widget.destroy()

    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = PentestChecklistGUI()
    app.run()
