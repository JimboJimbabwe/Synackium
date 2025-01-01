import tkinter as tk
from tkinter import ttk, filedialog
import json
import subprocess
import os
from pathlib import Path

class VulnerabilityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vulnerability Scanner")
        self.root.geometry("800x600")
        
        self.tests = self.load_tests()
        self.current_test_index = 0
        self.selected_folder = tk.StringVar()
        
        self.setup_gui()
        
    def load_tests(self):
        tests_data = {
            "open_redirection": {
                "paths": [],
                "scan_results_name": "open_redirection_results.txt"
            },
            "cookie_manipulation": {
                "paths": [],
                "scan_results_name": "cookie_manipulation_results.txt"
            },
            "javascript_injection": {
                "paths": ["/home/kali/Desktop/DOMENUMFOLDER/news/vulnquerier.py"],
                "scan_results_name": "javascript_injection_results.txt"
            },
            "document_domain_manipulation": {
                "paths": [],
                "scan_results_name": "domain_manipulation_results.txt"
            },
            "websocket_url_poisoning": {
                "paths": [],
                "scan_results_name": "websocket_poisoning_results.txt"
            },
            "link_manipulation": {
                "paths": [],
                "scan_results_name": "link_manipulation_results.txt"
            },
            "web_message_manipulation": {
                "paths": [],
                "scan_results_name": "web_message_results.txt"
            },
            "ajax_request_header_manipulation": {
                "paths": [],
                "scan_results_name": "ajax_manipulation_results.txt"
            },
            "local_file_path_manipulation": {
                "paths": [],
                "scan_results_name": "file_path_results.txt"
            },
            "client_side_sql_injection": {
                "paths": [],
                "scan_results_name": "sql_injection_results.txt"
            },
            "html5_storage_manipulation": {
                "paths": [],
                "scan_results_name": "storage_manipulation_results.txt"
            },
            "client_side_xpath_injection": {
                "paths": [],
                "scan_results_name": "xpath_injection_results.txt"
            },
            "client_side_json_injection": {
                "paths": [],
                "scan_results_name": "json_injection_results.txt"
            },
            "dom_data_manipulation": {
                "paths": [],
                "scan_results_name": "dom_manipulation_results.txt"
            }
        }
        return tests_data
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        folder_frame = ttk.LabelFrame(main_frame, text="Endpoint Selection", padding="5")
        folder_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(folder_frame, textvariable=self.selected_folder).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(folder_frame, text="Choose Folder", command=self.choose_folder).grid(row=0, column=1, padx=5)
        
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(nav_frame, text="←", command=self.previous_test).grid(row=0, column=0, padx=5)
        self.test_label = ttk.Label(nav_frame, text=list(self.tests.keys())[0], font=('Arial', 12, 'bold'))
        self.test_label.grid(row=0, column=1, padx=20)
        ttk.Button(nav_frame, text="→", command=self.next_test).grid(row=0, column=2, padx=5)
        
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", padding="5")
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.results_text = tk.Text(results_frame, height=20, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        ttk.Button(main_frame, text="Run Test", command=self.run_test).grid(row=3, column=0, columnspan=3, pady=10)
        
    def choose_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder.set(folder_path)
            
    def next_test(self):
        test_keys = list(self.tests.keys())
        self.current_test_index = (self.current_test_index + 1) % len(test_keys)
        self.update_test_label()
        
    def previous_test(self):
        test_keys = list(self.tests.keys())
        self.current_test_index = (self.current_test_index - 1) % len(test_keys)
        self.update_test_label()
        
    def update_test_label(self):
        test_keys = list(self.tests.keys())
        self.test_label.config(text=test_keys[self.current_test_index])
        
    def run_test(self):
        if not self.selected_folder.get():
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Please select a folder first.")
            return
            
        try:
            current_test = list(self.tests.keys())[self.current_test_index]
            test_info = self.tests[current_test]
            script_path = "vulnquerier.py"
            
            endpoint_path = self.selected_folder.get()
            results_path = os.path.join(endpoint_path, test_info["scan_results_name"])
            
            result = subprocess.run(
                ["python3", script_path, endpoint_path, results_path],
                capture_output=True,
                text=True
            )
            
            self.results_text.delete(1.0, tk.END)
            if result.stdout:
                self.results_text.insert(tk.END, result.stdout)
            if result.stderr:
                self.results_text.insert(tk.END, "\nErrors:\n" + result.stderr)
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error running test: {str(e)}")

def main():
    root = tk.Tk()
    app = VulnerabilityScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
