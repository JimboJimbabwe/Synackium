# dom_file_path_scanner.py
import os
import re
import argparse
from pathlib import Path

FILE_PATH_SINKS = [
    r'FileReader\.readAsArrayBuffer\s*\(',
    r'FileReader\.readAsBinaryString\s*\(',
    r'FileReader\.readAsDataURL\s*\(',
    r'FileReader\.readAsText\s*\(',
    r'FileReader\.readAsFile\s*\(',
    r'FileReader\.root\.getFile\s*\(',
    r'createObjectURL\s*\(',
    r'webkitRequestFileSystem\s*\(',
    r'requestFileSystem\s*\(',
    r'resolveLocalFileSystemURL\s*\(',
    r'openFile\s*\(',
    r'saveAs\s*\(',
    r'file:///',
    r'new File\s*\(',
    r'new Blob\s*\('
]

DANGEROUS_PATH_PATTERNS = [
    r'\.\.',                          # Directory traversal
    r'/',                            # Path separator
    r'\\',                           # Windows path separator
    r'%2e%2e',                       # URL encoded ../
    r'%2f',                          # URL encoded /
    r'~',                            # Home directory
    r'file[:\\/]',                   # file: protocol
    r'(C|D|E|F):[\\\/]',            # Windows drives
    r'/etc/',                        # Unix system directory
    r'/var/',                        # Unix variable directory
    r'/proc/',                       # Unix process directory
    r'System32',                     # Windows system directory
    r'\.exe$',                       # Executable files
    r'\.dll$',                       # DLL files
    r'\.sys$'                        # System files
]

USER_INPUT_SOURCES = [
    r'location\.',
    r'document\.URL',
    r'document\.documentURI',
    r'document\.baseURI',
    r'document\.referrer',
    r'window\.name',
    r'\.search',
    r'\.hash',
    r'\.pathname',
    r'input\.value',
    r'querySelector',
    r'getElementById'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in FILE_PATH_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 75)
                end = min(len(content), match.end() + 75)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for dangerous patterns and user input
                dangerous_patterns_found = []
                user_input_found = []
                
                for pattern in DANGEROUS_PATH_PATTERNS:
                    if re.search(pattern, context):
                        dangerous_patterns_found.append(pattern)
                
                for source in USER_INPUT_SOURCES:
                    if re.search(source, context):
                        user_input_found.append(source)
                
                # Risk assessment
                risk = 'LOW'
                if dangerous_patterns_found and user_input_found:
                    risk = 'HIGH'
                elif dangerous_patterns_found or user_input_found:
                    risk = 'MEDIUM'
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'dangerous_patterns': dangerous_patterns_found,
                    'user_input_sources': user_input_found,
                    'operation_type': 'READ' if 'read' in sink.lower() else 'WRITE'
                })
    
    return findings

def scan_directory(directory, verbose=False):
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                file_path = Path(root) / file
                if verbose:
                    print(f"Scanning {file_path}")
                findings = analyze_js_file(file_path)
                if findings:
                    results[str(file_path)] = findings
    
    return results

def generate_report(results, output_file):
    with open(output_file, 'w') as f:
        f.write("DOM-Based Local File Path Manipulation Vulnerability Report\n")
        f.write("====================================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nFile Path Manipulation Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    f.write(f"Operation Type: {finding['operation_type']}\n")
                    
                    if finding['dangerous_patterns']:
                        f.write("Dangerous Path Patterns Found:\n")
                        for pattern in finding['dangerous_patterns']:
                            f.write(f"  - {pattern}\n")
                    
                    if finding['user_input_sources']:
                        f.write("User Input Sources Found:\n")
                        for source in finding['user_input_sources']:
                            f.write(f"  - {source}\n")
                    
                    f.write(f"Context:\n{finding['context']}\n")
                    f.write("-" * 50 + "\n")
        
        # Summary statistics
        total_files = len(results)
        total_vulnerabilities = sum(len(findings) for findings in results.values())
        high_risk = sum(1 for findings in results.values() 
                       for finding in findings if finding['risk'] == 'HIGH')
        medium_risk = sum(1 for findings in results.values() 
                         for finding in findings if finding['risk'] == 'MEDIUM')
        
        # Operation type statistics
        read_ops = sum(1 for findings in results.values() 
                      for finding in findings if finding['operation_type'] == 'READ')
        write_ops = sum(1 for findings in results.values() 
                       for finding in findings if finding['operation_type'] == 'WRITE')
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")
        f.write(f"Medium Risk Vulnerabilities: {medium_risk}\n")
        f.write("\nOperation Types Breakdown:\n")
        f.write(f"Read Operations: {read_ops}\n")
        f.write(f"Write Operations: {write_ops}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based Local File Path Manipulation Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='file_path_manipulation_report.txt', 
                        help='Output file name (default: file_path_manipulation_report.txt)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Print verbose output during scanning')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        return
    
    if args.verbose:
        print(f"Starting scan of {args.path}")
    
    results = scan_directory(args.path, args.verbose)
    generate_report(results, args.output)
    
    if args.verbose:
        print(f"Scan complete. Found vulnerabilities in {len(results)} files")
        print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()