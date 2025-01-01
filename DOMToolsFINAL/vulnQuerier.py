import os

def analyze_vulnerability_report(scan_dir=None, report_file=None):
    if not scan_dir or not report_file:
        print("Please provide both scan directory and report file path")
        return
        
    # Convert paths to absolute
    scan_dir = os.path.abspath(scan_dir)
    report_file = os.path.abspath(report_file)
    
    if not os.path.isdir(scan_dir):
        print(f"Error: Directory '{scan_dir}' not found")
        return
        
    try:
        with open(report_file, 'r') as f:
            content = f.read()
        
        file_sections = content.split('\nFile: ')[1:]
        
        results = {}
        for section in file_sections:
            filename = section.split('\n')[0].strip()
            full_path = os.path.join(scan_dir, filename)
            
            sink_count = section.count('Vulnerable Sink:')
            results[full_path] = sink_count
            
        print(f"\nTotal files with vulnerabilities: {len(results)}")
        print("\nVulnerabilities per file:")
        for filepath, count in sorted(results.items()):
            print(f"{filepath}: {count} vulnerable sink(s)")
            
        return results
        
    except FileNotFoundError:
        print(f"Error: Report file '{report_file}' not found")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        analyze_vulnerability_report(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python script.py <scan_directory> <report_file>")
