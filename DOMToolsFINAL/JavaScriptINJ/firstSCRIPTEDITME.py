import os
import re
from pathlib import Path

DANGEROUS_SINKS = [
    r'eval\(',
    r'new Function\(',
    r'setTimeout\([^,]+,',
    r'setInterval\([^,]+,',
    r'setImmediate\(',
    r'execCommand\(',
    r'execScript\(',
    r'msSetImmediate\(',
    r'createContextualFragment\(',
    r'generateCRMFRequest\('
]

def analyze_js_file(file_path):
    vulnerabilities = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        line_number = 1
        
        for sink in DANGEROUS_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                # Get context (line before and after)
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                # Calculate line number
                line_number = content.count('\n', 0, match.start()) + 1
                
                vulnerabilities.append({
                    'sink': sink.replace('\\(', ''),
                    'line': line_number,
                    'context': context
                })
                
        # Check for user input sources
        user_inputs = [
            r'location\.',
            r'document\.URL',
            r'document\.documentURI',
            r'document\.URLUnencoded',
            r'document\.baseURI',
            r'document\.cookie',
            r'document\.referrer'
        ]
        
        for input_source in user_inputs:
            if re.search(input_source, content):
                for vuln in vulnerabilities:
                    if input_source in vuln['context']:
                        vuln['risk'] = 'HIGH'
                    else:
                        vuln['risk'] = 'MEDIUM'

    return vulnerabilities

def scan_directory(directory):
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                file_path = Path(root) / file
                vulnerabilities = analyze_js_file(file_path)
                if vulnerabilities:
                    results[str(file_path)] = vulnerabilities
    
    return results

def generate_report(results):
    with open('vulnerability_report.txt', 'w') as f:
        f.write("JavaScript Injection Vulnerability Report\n")
        f.write("=====================================\n\n")
        
        for file_path, vulns in results.items():
            if vulns:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for vuln in vulns:
                    f.write(f"\nVulnerable Sink: {vuln['sink']}\n")
                    f.write(f"Line Number: {vuln['line']}\n")
                    f.write(f"Risk Level: {vuln.get('risk', 'MEDIUM')}\n")
                    f.write(f"Context:\n{vuln['context']}\n")
                    f.write("-" * 50 + "\n")

if __name__ == "__main__":
    directory = input("Enter the directory path to scan: ")
    results = scan_directory(directory)
    generate_report(results)
    print("Scan complete. Results written to vulnerability_report.txt")