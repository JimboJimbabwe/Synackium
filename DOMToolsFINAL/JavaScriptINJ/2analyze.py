def analyze_vulnerability_report(report_path):
   with open(report_path, 'r') as f:
       content = f.read()
   
   # Split into file sections
   file_sections = content.split('\nFile: ')[1:]  # Skip header
   
   results = {}
   for section in file_sections:
       # Get filename from first line
       filename = section.split('\n')[0].strip()
       
       # Count vulnerable sinks
       sink_count = section.count('Vulnerable Sink:')
       
       results[filename] = sink_count

   # Print summary
   print(f"\nTotal files with vulnerabilities: {len(results)}")
   print("\nVulnerabilities per file:")
   for filename, count in results.items():
       print(f"{filename}: {count} vulnerable sink(s)")

if __name__ == "__main__":
   analyze_vulnerability_report('vulnerability_report.txt')