import win32api
import win32con
import time
import sys
import keyboard

class CoordinateCapture:
    def __init__(self):
        self.coordinates = {
            "WebpageAck": None,
            "NullClick": None,
            "SaveWindow": None,
            "FilenameBox": None,
            "DirectoryBar": None,
            "SaveButton": None,
            "CloseWindow": None
        }
        self.current_var = None
        self.running = True

    def get_mouse_position(self):
        return win32api.GetCursorPos()

    def is_left_click(self):
        return win32api.GetKeyState(win32con.VK_LBUTTON) < 0

    def is_right_click(self):
        return win32api.GetKeyState(win32con.VK_RBUTTON) < 0

    def capture_coordinates(self, var_name):
        print(f"\nPlease left-click to store the {var_name} coordinates.")
        print("Right-click when done to move to the next position.")
        
        self.current_var = var_name
        last_left_state = False
        last_right_state = False

        while True:
            if keyboard.is_pressed('esc'):
                print("\nCapture cancelled.")
                return False

            current_left_state = self.is_left_click()
            current_right_state = self.is_right_click()

            # Detect left click (on button release)
            if last_left_state and not current_left_state:
                x, y = self.get_mouse_position()
                self.coordinates[self.current_var] = (x, y)
                print(f"Coordinates for {self.current_var} recorded at: {x}, {y}")

            # Detect right click (on button release)
            if last_right_state and not current_right_state:
                return True

            last_left_state = current_left_state
            last_right_state = current_right_state
            time.sleep(0.01)  # Reduce CPU usage

    def run(self):
        print("=== Mouse Coordinate Capture Tool ===")
        print("This tool will help you capture screen coordinates.")
        print("For each position:")
        print("1. Left-click to record coordinates")
        print("2. Right-click to move to the next position")
        print("Press ESC at any time to exit.")
        
        try:
            for var_name in self.coordinates.keys():
                if not self.capture_coordinates(var_name):
                    print("\nCoordinate capture interrupted.")
                    break
            
            print("\nCapture complete! Final coordinates:")
            for name, coords in self.coordinates.items():
                print(f"{name}: {coords}")
            
            # Save coordinates to a file
            with open('coordinates.txt', 'w') as f:
                f.write("# Mouse coordinates captured on: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
                for name, coords in self.coordinates.items():
                    f.write(f"{name}: {coords}\n")
            print("\nCoordinates have been saved to 'coordinates.txt'")
            
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            sys.exit(0)
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Check if required modules are installed
    try:
        import win32api
        import win32con
        import keyboard
    except ImportError:
        print("Required modules not found. Please install them using:")
        print("pip install pywin32 keyboard")
        sys.exit(1)

    capture_tool = CoordinateCapture()
    capture_tool.run()
