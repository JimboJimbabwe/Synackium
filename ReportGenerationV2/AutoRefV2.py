import win32api
import win32con
import keyboard
import json
import time
import os
from typing import Dict, List, Tuple
import pyautogui

class ReportAutomation:
    def __init__(self, json_file: str):
        self.coordinates = {
            "title": (727, 225),
            "description": (739, 306),
            "attachment": (816, 448),
            "filename": (320, 532),
            "open": (565, 561)
        }
        self.current_step = 1
        self.json_data = self.load_json(json_file)
        
    def load_json(self, json_file: str) -> List[Dict]:
        """Load and parse the JSON file."""
        with open(json_file, 'r') as f:
            return json.load(f)
    
    def click_coordinate(self, x: int, y: int, action_name: str):
        """Move to and click at specified coordinates."""
        print(f"Clicking {action_name} at coordinates ({x}, {y})")
        win32api.SetCursorPos((x, y))
        time.sleep(0.5)  # Small delay before click
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def type_text(self, text: str, field_name: str):
        """Type the specified text."""
        print(f"Typing into {field_name}: {text}")
        pyautogui.write(text)

    def format_image_paths(self, images: List[str]) -> str:
        """
        Simply extracts and quotes the filenames from the full paths.
        Returns them as a comma-separated string.
        """
        filenames = [f'"{os.path.basename(img)}"' for img in images]
        return ' '.join(filenames)

    def process_step(self, step_data: Dict):
        """Process a single step in the report."""
        print(f"\nProcessing Step {step_data['Step']}")
        print(f"Action: {step_data['Action']}")
        print(f"Images to process: {', '.join(step_data['ReferenceImages'])}")
        
        # Click and fill title
        print("\n1. Processing Title...")
        self.click_coordinate(*self.coordinates["title"], "title box")
        time.sleep(3)
        self.type_text(step_data["ImageTitle"], "title")
        time.sleep(2)
        self.click_coordinate(*self.coordinates["title"], "title box")

        # Click and fill description
        print("\n2. Processing Description...")
        self.click_coordinate(*self.coordinates["description"], "description box")
        time.sleep(3)
        self.type_text(step_data["ImageDescription"], "description")
        time.sleep(2)

        # Process images
        print("\n3. Processing images...")
        # Click attachment box
        print("  - Clicking attachment box...")
        self.click_coordinate(*self.coordinates["attachment"], "attachment box")
        time.sleep(3)
        
        # Click filename box and enter formatted image paths
        print("  - Entering filenames...")
        self.click_coordinate(*self.coordinates["filename"], "filename box")
        time.sleep(3)
        formatted_paths = self.format_image_paths(step_data["ReferenceImages"])
        self.type_text(formatted_paths, "filename")
        time.sleep(2)
        
        # Click open button
        print("  - Clicking open button...")
        self.click_coordinate(*self.coordinates["open"], "open button")
        time.sleep(3)

    def run(self):
        """Run the automation process."""
        print("=== Pentest Report Automation ===")
        print("Press Left Shift to proceed to next step")
        print("Press ESC to exit")
        
        while True:
            try:
                # Find current step data
                step_data = next((step for step in self.json_data 
                                if step["Step"] == self.current_step), None)
                
                if not step_data:
                    print(f"\nNo more steps found. Completed {self.current_step-1} steps.")
                    break

                print(f"\n{'='*50}")
                print(f"Ready to process Step {self.current_step}")
                print(f"This step will process these images: {step_data['ReferenceImages']}")
                print("Press Left Shift to continue...")
                print(f"{'='*50}")
                
                # Wait for left shift
                while True:
                    if keyboard.is_pressed('left shift'):
                        time.sleep(0.5)  # Debounce
                        break
                    if keyboard.is_pressed('esc'):
                        print("\nProcess terminated by user.")
                        return
                    time.sleep(0.1)

                # Process the step
                self.process_step(step_data)
                print(f"\nCompleted Step {self.current_step}")
                
                self.current_step += 1
                time.sleep(1)  # Brief pause between steps

            except KeyboardInterrupt:
                print("\nProcess interrupted by user.")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                break

if __name__ == "__main__":
    try:
        # Initialize automation with JSON file
        automation = ReportAutomation('MissionBank.json')
        automation.run()
    except Exception as e:
        print(f"Error: {e}")
