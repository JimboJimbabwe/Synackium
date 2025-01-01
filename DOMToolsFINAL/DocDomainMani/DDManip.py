# dom_domain_scanner.py
import os
import re
import argparse
from pathlib import Path

DOMAIN_SINKS = [
    r'document\.domain\s*=',
    r'document\[[\'"]*domain[\'"]*\]\s*=',
    r'setDomain\(',
    r'\.domain\s*=',
    r'window\.document\.domain'
]

SUSPICIOUS_PATTERNS = [
    r'\.(com|org|net|edu|gov|mil|io|ai)',  # Common TLDs
    r'localhost',
    r'127\.0\.0\.1',
    r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
    r'document\.referrer',
    r'location\.',
    r'window\.name'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in DOMAIN_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for suspicious patterns in context
                suspicious_found = []
                for pattern in SUSPICIOUS_PATTERNS:
                    if re.search(pattern, context):
                        suspicious_found.append(pattern)
                
                risk = 'HIGH' if suspicious_found else 'MEDIUM'
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'suspicious_patterns': suspicious_found
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
        f.write("DOM-Based Document Domain Manipulation Vulnerability Report\n")
        f.write("===================================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nDomain Manipulation Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    if finding['suspicious_patterns']:
                        f.write("Suspicious Patterns Found:\n")
                        for pattern in finding['suspicious_patterns']:
                            f.write(f"  - {pattern}\n")
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
    parser = argparse.ArgumentParser(description='DOM-Based Document Domain Manipulation Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='domain_manipulation_report.txt', 
                        help='Output file name (default: domain_manipulation_report.txt)')
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