while read file; do python3 curlLaunch.py "$file"; sleep 15; done < CMDs.txt

# If CMDs.txt is in the same directory as curlLaunch.py:
while read file; do python3 curlLaunch.py "$file"; sleep 15; done < CMDs.txt

# If CMDs.txt is in a different directory and contains full paths:
while read file; do cd $(dirname "$file") && python3 /path/to/curlLaunch.py "$file"; sleep 15; done < CMDs.txt

# If CMDs.txt contains relative paths from a base directory:
base_dir="/path/to/base/directory"
while read file; do cd "$base_dir" && python3 curlLaunch.py "$file"; sleep 15; done < CMDs.txt

For the basic version (CMDs.txt in same directory as curlLaunch.py):
batchCopyfor /F "tokens=*" %%f in (CMDs.txt) do (
    python curlLaunch.py "%%f"
    timeout /t 15 /nobreak
)
For handling files in different directories (if CMDs.txt contains full paths):
batchCopyfor /F "tokens=*" %%f in (CMDs.txt) do (
    pushd "%%~dpf"
    python "C:\path\to\curlLaunch.py" "%%f"
    popd
    timeout /t 15 /nobreak
)
For using relative paths from a base directory:
batchCopyset "base_dir=C:\path\to\base\directory"
for /F "tokens=*" %%f in (CMDs.txt) do (
    pushd "%base_dir%"
    python curlLaunch.py "%%f"
    popd
    timeout /t 15 /nobreak
)
Key differences from the bash version:

for /F replaces while read
%%f is the Windows variable syntax (use single % if running directly in CMD)
timeout /t 15 /nobreak replaces sleep 15
pushd/popd replaces cd for directory changes (and automatically handles returning to the original directory)
Windows paths use backslashes instead of forward slashes

Save these scripts with a .bat extension (e.g., process_files.bat) and run them from the command prompt.
