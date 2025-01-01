import os
import re
import argparse
from pathlib import Path

REDIRECTION_SINKS = [
    r'location\s*=',
    r'location\.href\s*=',
    r'location\.replace\(',
    r'location\.assign\(',
    r'window\.location\s*=',
    r'window\.navigate\(',
    r'element\.href\s*=',
    r'element\.src\s*=',
    r'element\.action\s*=',
]

USER_INPUT_SOURCES = [
    r'location\.hash',
    r'location\.search',
    r'location\.href',
    r'document\.URL',
    r'document\.documentURI',
    r'document\.referrer',
    r'window\.name'
]

def analyze_js_file(file_path):
    redirections = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in REDIRECTION_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                risk = 'MEDIUM'
                for input_source in USER_INPUT_SOURCES:
                    if re.search(input_source, context):
                        risk = 'HIGH'
                        break
                
                redirections.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'has_user_input': risk == 'HIGH'
                })
    
    return redirections

def scan_directory(directory):
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                file_path = Path(root) / file
                redirections = analyze_js_file(file_path)
                if redirections:
                    results[str(file_path)] = redirections
    
    return results

def generate_report(results, output_file):
    with open(output_file, 'w') as f:
        f.write("DOM-Based Open Redirection Vulnerability Report\n")
        f.write("==========================================\n\n")
        
        for file_path, redirects in results.items():
            if redirects:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for redirect in redirects:
                    f.write(f"\nRedirection Sink: {redirect['sink']}\n")
                    f.write(f"Line Number: {redirect['line']}\n")
                    f.write(f"Risk Level: {redirect['risk']}\n")
                    f.write(f"Uses User Input: {'Yes' if redirect['has_user_input'] else 'No'}\n")
                    f.write(f"Context:\n{redirect['context']}\n")
                    f.write("-" * 50 + "\n")
        
        total_files = len(results)
        total_vulnerabilities = sum(len(redirects) for redirects in results.values())
        high_risk = sum(1 for redirects in results.values() 
                       for redirect in redirects if redirect['risk'] == 'HIGH')
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based Open Redirection Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='open_redirection_report.txt', 
                        help='Output file name (default: open_redirection_report.txt)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Print verbose output during scanning')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        return
    
    if args.verbose:
        print(f"Starting scan of {args.path}")
    
    results = scan_directory(args.path)
    generate_report(results, args.output)
    
    if args.verbose:
        print(f"Scan complete. Found vulnerabilities in {len(results)} files")
        print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()