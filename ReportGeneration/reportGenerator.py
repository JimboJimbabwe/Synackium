import tkinter as tk
from tkinter import ttk, scrolledtext
import os


class ReportGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pentest Report Generator")
        self.root.geometry("800x600")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Create frames for each state
        self.intro_frame = ttk.Frame(self.notebook)
        self.method_frame = ttk.Frame(self.notebook)
        self.concl_frame = ttk.Frame(self.notebook)

        # Add frames to notebook
        self.notebook.add(self.intro_frame, text='Introduction')
        self.notebook.add(self.method_frame, text='Methodology')
        self.notebook.add(self.concl_frame, text='Conclusion')

        self.setup_introduction_tab()
        self.setup_methodology_tab()
        self.setup_conclusion_tab()

        # Create initial files if they don't exist
        self.create_initial_files()

    def create_initial_files(self):
        intro_content = """##### What are we testing? 

##### Why are we testing this?

##### How will this be accomplished?

Sources Cited:
"""
        method_content = """##### Assets Tested:

##### Tools Used:

##### Steps:
"""
        concl_content = """The application is: 

##### Testing Conducted:
"""

        files = {
            'FinalIntroduction.txt': intro_content,
            'FinalMethodology.txt': method_content,
            'FinalConclusion.txt': concl_content
        }

        for filename, content in files.items():
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write(content)

    def setup_introduction_tab(self):
        # Create and pack widgets for Introduction
        labels = ['What:', 'Why:', 'How:', 'Sources:']
        self.intro_texts = {}

        for label in labels:
            frame = ttk.Frame(self.intro_frame)
            frame.pack(fill='x', padx=5, pady=5)

            ttk.Label(frame, text=label).pack(side='left')
            text = scrolledtext.ScrolledText(frame, height=4, width=70)
            text.pack(side='left', padx=5)
            self.intro_texts[label] = text

            # Bind Shift+Enter
            text.bind('<Shift-Return>', lambda e: 'break')

        ttk.Button(self.intro_frame, text="Push to Final",
                   command=self.push_introduction).pack(pady=10)

    def setup_methodology_tab(self):
        # Create and pack widgets for Methodology
        labels = ['Assets:', 'Tools:', 'Steps:']
        self.method_texts = {}

        for label in labels:
            frame = ttk.Frame(self.method_frame)
            frame.pack(fill='x', padx=5, pady=5)

            ttk.Label(frame, text=label).pack(side='left')
            text = scrolledtext.ScrolledText(frame, height=4, width=70)
            text.pack(side='left', padx=5)
            self.method_texts[label] = text

            # Bind Shift+Enter
            text.bind('<Shift-Return>', lambda e: 'break')

        ttk.Button(self.method_frame, text="Push to Final",
                   command=self.push_methodology).pack(pady=10)

    def setup_conclusion_tab(self):
        # Create vulnerability button frame
        btn_frame = ttk.Frame(self.concl_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(btn_frame, text="Vulnerable",
                   command=lambda: self.set_vulnerability("Vulnerable")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Not Vulnerable",
                   command=lambda: self.set_vulnerability("Not Vulnerable")).pack(side='left')

        # Create conclusion text area
        self.concl_text = scrolledtext.ScrolledText(self.concl_frame, height=10, width=70)
        self.concl_text.pack(padx=5, pady=5)

        # Bind Shift+Enter
        self.concl_text.bind('<Shift-Return>', lambda e: 'break')

        ttk.Button(self.concl_frame, text="Push to Final",
                   command=self.push_conclusion).pack(pady=10)

    def push_introduction(self):
        with open('FinalIntroduction.txt', 'r') as f:
            content = f.read()

        # Update each section
        sections = {
            'What:': '##### What are we testing?',
            'Why:': '##### Why are we testing this?',
            'How:': '##### How will this be accomplished?',
            'Sources:': 'Sources Cited:'
        }

        for label, marker in sections.items():
            text = self.intro_texts[label].get('1.0', 'end-1c').strip()
            if text:
                content = self.insert_after_marker(content, marker, text)

        with open('FinalIntroduction.txt', 'w') as f:
            f.write(content)

    def push_methodology(self):
        with open('FinalMethodology.txt', 'r') as f:
            content = f.read()

        # Update each section with numbered lists
        sections = {
            'Assets:': '##### Assets Tested:',
            'Tools:': '##### Tools Used:',
            'Steps:': '##### Steps:'
        }

        for label, marker in sections.items():
            text = self.method_texts[label].get('1.0',
                                                'end-1c').strip()  # Fixed: Changed from intro_texts to method_texts
            if text:
                # Convert to numbered list
                lines = text.split('\n')
                numbered_text = '\n'.join(f"{i + 1}. {line}" for i, line in enumerate(lines) if line.strip())
                content = self.insert_after_marker(content, marker, numbered_text)

        with open('FinalMethodology.txt', 'w') as f:
            f.write(content)

    def set_vulnerability(self, status):
        with open('FinalConclusion.txt', 'r') as f:
            content = f.read()

        content = self.insert_after_marker(content, "The application is:", status)

        with open('FinalConclusion.txt', 'w') as f:
            f.write(content)

    def push_conclusion(self):
        with open('FinalConclusion.txt', 'r') as f:
            content = f.read()

        text = self.concl_text.get('1.0', 'end-1c').strip()
        if text:
            content = self.insert_after_marker(content, "##### Testing Conducted:", text)

        with open('FinalConclusion.txt', 'w') as f:
            f.write(content)

    def insert_after_marker(self, content, marker, new_text):
        """Insert text after a marker with proper formatting"""
        parts = content.split(marker)
        if len(parts) < 2:
            return content

        return f"{parts[0]}{marker}\n\n{new_text}\n\n{''.join(parts[1:]).lstrip()}"


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGUI(root)
    root.mainloop()
