#!/usr/bin/python3
import os
from pathlib import Path
import argparse

def create_txt_list(parent_folder):
    """Create CMDs.txt in each subfolder listing all txt files"""
    parent_path = Path(parent_folder)
    
    # Get all immediate subfolders
    subfolders = [f for f in parent_path.iterdir() if f.is_dir()]
    
    for subfolder in subfolders:
        # Get all txt files in this subfolder
        txt_files = [f.name for f in subfolder.glob("*.txt") if f.is_file() and f.name != "CMDs.txt"]
        
        if txt_files:  # Only create CMDs.txt if there are txt files
            # Sort files for consistent ordering
            txt_files.sort()
            
            # Create CMDs.txt in the subfolder
            cmd_file = subfolder / "CMDs.txt"
            with open(cmd_file, 'w') as f:
                f.write('\n'.join(txt_files))
            
            print(f"Created {cmd_file} with {len(txt_files)} entries")
        else:
            print(f"No txt files found in {subfolder}")

def main():
    parser = argparse.ArgumentParser(description='Create CMDs.txt listing all txt files in each subfolder')
    parser.add_argument('parent_folder', help='Parent folder containing subfolders to process')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.parent_folder):
        print(f"Error: {args.parent_folder} is not a directory")
        return
    
    create_txt_list(args.parent_folder)

if __name__ == "__main__":
    main()
