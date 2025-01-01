# dom_link_scanner.py
import os
import re
import argparse
from pathlib import Path

LINK_SINKS = [
    r'\.href\s*=',
    r'\.src\s*=',
    r'\.action\s*=',
    r'setAttribute\([\'"]href[\'"]\s*,',
    r'setAttribute\([\'"]src[\'"]\s*,',
    r'setAttribute\([\'"]action[\'"]\s*,',
    r'window\.open\(',
    r'\.replace\(',
    r'\.assign\(',
    r'\.navigate\('
]

SUSPICIOUS_PATTERNS = [
    r'javascript:',
    r'data:',
    r'vbscript:',
    r'file:',
    r'chrome:',
    r'about:',
    r'localhost',
    r'127\.0\.0\.1',
    r'document\.write',
    r'innerHTML',
    r'outerHTML'
]

USER_INPUT_SOURCES = [
    r'location\.',
    r'document\.URL',
    r'document\.documentURI',
    r'document\.referrer',
    r'window\.name',
    r'\.search',
    r'\.hash',
    r'\.pathname'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in LINK_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for suspicious patterns and user input
                suspicious_found = []
                user_input_found = []
                
                for pattern in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, context):
                        suspicious_found.append(pattern)
                
                for source in USER_INPUT_SOURCES:
                    if re.search(source, context):
                        user_input_found.append(source)
                
                # Determine risk level
                risk = 'LOW'
                if suspicious_found:
                    risk = 'HIGH'
                elif user_input_found:
                    risk = 'MEDIUM'
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'suspicious_patterns': suspicious_found,
                    'user_input_sources': user_input_found
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
        f.write("DOM-Based Link Manipulation Vulnerability Report\n")
        f.write("=========================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nLink Manipulation Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    
                    if finding['suspicious_patterns']:
                        f.write("Suspicious Patterns Found:\n")
                        for pattern in finding['suspicious_patterns']:
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
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")
        f.write(f"Medium Risk Vulnerabilities: {medium_risk}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based Link Manipulation Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='link_manipulation_report.txt', 
                        help='Output file name (default: link_manipulation_report.txt)')
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