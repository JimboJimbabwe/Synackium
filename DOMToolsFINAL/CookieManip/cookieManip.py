# dom_cookie_scanner.py
import os
import re
import argparse
from pathlib import Path

COOKIE_SINKS = [
    r'document\.cookie\s*=',
    r'document\.cookie\.set',
    r'setCookie\(',
    r'\.cookie\s*=',
    r'Cookie\.set',
    r'cookies\.set',
    r'\.setCookie'
]

USER_INPUT_SOURCES = [
    r'location\.hash',
    r'location\.search',
    r'location\.href',
    r'document\.URL',
    r'document\.documentURI',
    r'document\.referrer',
    r'window\.name',
    r'localStorage',
    r'sessionStorage'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in COOKIE_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                risk = 'MEDIUM'
                input_sources_found = []
                for input_source in USER_INPUT_SOURCES:
                    if re.search(input_source, context):
                        risk = 'HIGH'
                        input_sources_found.append(input_source)
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'input_sources': input_sources_found,
                    'has_user_input': len(input_sources_found) > 0
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
        f.write("DOM-Based Cookie Manipulation Vulnerability Report\n")
        f.write("=============================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nCookie Manipulation Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    if finding['input_sources']:
                        f.write("User Input Sources Found:\n")
                        for source in finding['input_sources']:
                            f.write(f"  - {source}\n")
                    f.write(f"Context:\n{finding['context']}\n")
                    f.write("-" * 50 + "\n")
        
        # Summary statistics
        total_files = len(results)
        total_vulnerabilities = sum(len(findings) for findings in results.values())
        high_risk = sum(1 for findings in results.values() 
                       for finding in findings if finding['risk'] == 'HIGH')
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based Cookie Manipulation Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='cookie_manipulation_report.txt', 
                        help='Output file name (default: cookie_manipulation_report.txt)')
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