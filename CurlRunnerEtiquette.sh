while read file; do python3 curlLaunch.py "$file"; sleep 15; done < CMDs.txt

# If CMDs.txt is in the same directory as curlLaunch.py:
while read file; do python3 curlLaunch.py "$file"; sleep 15; done < CMDs.txt

# If CMDs.txt is in a different directory and contains full paths:
while read file; do cd $(dirname "$file") && python3 /path/to/curlLaunch.py "$file"; sleep 15; done < CMDs.txt

# If CMDs.txt contains relative paths from a base directory:
base_dir="/path/to/base/directory"
while read file; do cd "$base_dir" && python3 curlLaunch.py "$file"; sleep 15; done < CMDs.txt
