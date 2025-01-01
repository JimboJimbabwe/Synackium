# dom_json_scanner.py
import os
import re
import argparse
from pathlib import Path

JSON_SINKS = [
    r'JSON\.parse\s*\(',
    r'jQuery\.parseJSON\s*\(',
    r'\$\.parseJSON\s*\(',
    r'JSON\.stringify\s*\(',
    r'\.json\s*\(',
    r'\.getJSON\s*\(',
    r'\.parseJSON\s*\(',
]

DANGEROUS_PATTERNS = [
    r'__proto__',                    # Prototype pollution
    r'constructor',                  # Constructor access
    r'prototype',                    # Prototype access
    r'\[\s*[\'"].*?[\'"]\s*\]',     # Array access with string
    r'eval\s*\(',                    # Eval usage
    r'Function\s*\(',                # Dynamic function creation
    r'\{\s*["\']\s*\+',             # Object key concatenation
    r'\+\s*["\']\s*:',              # Object key concatenation
    r'\${.*?}',                      # Template literals
    r'require\s*\(',                 # Module loading
    r'process\.',                    # Node.js process object
    r'global\.',                     # Global object access
]

USER_INPUT_SOURCES = [
    r'location\.',
    r'document\.URL',
    r'window\.name',
    r'\.search',
    r'\.hash',
    r'\.value',
    r'localStorage',
    r'sessionStorage',
    r'getElementById\(',
    r'querySelector\(',
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in JSON_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for dangerous patterns and user input
                dangerous_found = []
                user_input_found = []
                
                for pattern in DANGEROUS_PATTERNS:
                    if re.search(pattern, context):
                        dangerous_found.append(pattern)
                
                for source in USER_INPUT_SOURCES:
                    if re.search(source, context):
                        user_input_found.append(source)
                
                # Check for direct string concatenation
                has_concat = re.search(r'[\'"]\s*\+|\+\s*[\'"]', context) is not None
                
                # Risk assessment
                risk = 'LOW'
                if dangerous_found and user_input_found:
                    risk = 'HIGH'
                elif dangerous_found or (user_input_found and has_concat):
                    risk = 'MEDIUM'
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'dangerous_patterns': dangerous_found,
                    'user_input_sources': user_input_found,
                    'uses_concatenation': has_concat,
                    'operation_type': 'parse' if 'parse' in sink.lower() else 'stringify',
                    'library': 'jQuery' if 'jQuery' in sink or '$.' in sink else 'native'
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
        f.write("DOM-Based JSON Injection Vulnerability Report\n")
        f.write("========================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nJSON Operation Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    f.write(f"Operation Type: {finding['operation_type']}\n")
                    f.write(f"Library Used: {finding['library']}\n")
                    f.write(f"Uses String Concatenation: {'Yes' if finding['uses_concatenation'] else 'No'}\n")
                    
                    if finding['dangerous_patterns']:
                        f.write("Dangerous Patterns Found:\n")
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
        
        # Operation statistics
        parse_ops = sum(1 for findings in results.values() 
                       for finding in findings if finding['operation_type'] == 'parse')
        stringify_ops = sum(1 for findings in results.values() 
                          for finding in findings if finding['operation_type'] == 'stringify')
        
        # Library statistics
        jquery_usage = sum(1 for findings in results.values() 
                         for finding in findings if finding['library'] == 'jQuery')
        native_usage = sum(1 for findings in results.values() 
                         for finding in findings if finding['library'] == 'native')
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")
        f.write(f"Medium Risk Vulnerabilities: {medium_risk}\n")
        f.write("\nOperation Types Breakdown:\n")
        f.write(f"Parse Operations: {parse_ops}\n")
        f.write(f"Stringify Operations: {stringify_ops}\n")
        f.write("\nLibrary Usage Breakdown:\n")
        f.write(f"jQuery: {jquery_usage}\n")
        f.write(f"Native JSON: {native_usage}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based JSON Injection Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='json_injection_report.txt', 
                        help='Output file name (default: json_injection_report.txt)')
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