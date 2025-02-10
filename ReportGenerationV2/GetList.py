import os
import sys

folder_path = sys.argv[1]
png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]

with open('filenames.txt', 'w') as f:
   f.write('\n'.join(png_files))
   
with open('references.txt', 'w') as f:
   f.write('\n'.join(f"*Reference: {png}" for png in png_files))
