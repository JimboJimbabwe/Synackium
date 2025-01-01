# dom_ajax_header_scanner.py
import os
import re
import argparse
from pathlib import Path

AJAX_HEADER_SINKS = [
    r'setRequestHeader\s*\(',
    r'XMLHttpRequest\.open\s*\(',
    r'XMLHttpRequest\.send\s*\(',
    r'\.ajax\s*\(',
    r'\.ajaxSetup\s*\(',
    r'headers\s*:',
    r'beforeSend\s*:',
    r'$.ajax\s*\(',
    r'\$\.ajax\s*\(',
    r'fetch\s*\(',
    r'headers\s*:\s*new Headers\s*\('
]

SENSITIVE_HEADERS = [
    r'Authorization',
    r'X-API-Key',
    r'Cookie',
    r'X-CSRF',
    r'Origin',
    r'Host',
    r'Referer',
    r'X-Forwarded-For',
    r'User-Agent',
    r'Access-Control'
]

USER_INPUT_SOURCES = [
    r'location\.',
    r'document\.URL',
    r'window\.name',
    r'\.search',
    r'\.hash',
    r'\.pathname',
    r'localStorage',
    r'sessionStorage'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in AJAX_HEADER_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 75)  # Larger context for AJAX calls
                end = min(len(content), match.end() + 75)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for sensitive headers and user input
                sensitive_headers_found = []
                user_input_found = []
                
                for header in SENSITIVE_HEADERS:
                    if re.search(header, context):
                        sensitive_headers_found.append(header)
                
                for source in USER_INPUT_SOURCES:
                    if re.search(source, context):
                        user_input_found.append(source)
                
                # Risk assessment
                risk = 'LOW'
                if sensitive_headers_found and user_input_found:
                    risk = 'HIGH'
                elif sensitive_headers_found or user_input_found:
                    risk = 'MEDIUM'
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'sensitive_headers': sensitive_headers_found,
                    'user_input_sources': user_input_found,
                    'ajax_type': 'XMLHttpRequest' if 'XMLHttpRequest' in sink else 'jQuery' if '$' in sink else 'Fetch'
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
        f.write("DOM-Based Ajax Request-Header Manipulation Vulnerability Report\n")
        f.write("======================================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nAjax Header Manipulation Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    f.write(f"Ajax Type: {finding['ajax_type']}\n")
                    
                    if finding['sensitive_headers']:
                        f.write("Sensitive Headers Involved:\n")
                        for header in finding['sensitive_headers']:
                            f.write(f"  - {header}\n")
                    
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
        
        # Ajax type statistics
        xhr_count = sum(1 for findings in results.values() 
                       for finding in findings if finding['ajax_type'] == 'XMLHttpRequest')
        jquery_count = sum(1 for findings in results.values() 
                          for finding in findings if finding['ajax_type'] == 'jQuery')
        fetch_count = sum(1 for findings in results.values() 
                         for finding in findings if finding['ajax_type'] == 'Fetch')
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")
        f.write(f"Medium Risk Vulnerabilities: {medium_risk}\n")
        f.write("\nAjax Types Breakdown:\n")
        f.write(f"XMLHttpRequest: {xhr_count}\n")
        f.write(f"jQuery Ajax: {jquery_count}\n")
        f.write(f"Fetch API: {fetch_count}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based Ajax Request-Header Manipulation Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='ajax_header_manipulation_report.txt', 
                        help='Output file name (default: ajax_header_manipulation_report.txt)')
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