# dom_xpath_scanner.py
import os
import re
import argparse
from pathlib import Path

XPATH_SINKS = [
    r'document\.evaluate\s*\(',
    r'element\.evaluate\s*\(',
    r'evaluateXPath\s*\(',
    r'createExpression\s*\(',
    r'createNSResolver\s*\(',
    r'XPathEvaluator\s*\(',
    r'\.selectNodes\s*\(',
    r'\.selectSingleNode\s*\(',
    r'\.evaluate\s*\(',
    r'xpath\s*\=',
    r'\.xpathEvaluate\s*\('
]

XPATH_PATTERNS = [
    r'\/\/',                         # Double slash (descendant axis)
    r'\[\s*@',                       # Attribute selectors
    r'contains\s*\(',                # Contains function
    r'position\s*\(',                # Position function
    r'last\s*\(',                    # Last function
    r'text\s*\(',                    # Text function
    r'ancestor::|descendant::|following::|preceding::', # Axes
    r'\|\|',                         # String concatenation
    r'and|or|not',                   # Boolean operations
    r'\d+\s*=\s*\d+'                # Number comparisons
]

USER_INPUT_SOURCES = [
    r'location\.',
    r'document\.URL',
    r'window\.name',
    r'\.search',
    r'\.hash',
    r'\.value',
    r'getElementById\(',
    r'querySelector\(',
    r'getAttribute\(',
    r'dataset\.'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in XPATH_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for XPath patterns and user input
                xpath_patterns_found = []
                user_input_found = []
                string_concat = False
                
                for pattern in XPATH_PATTERNS:
                    if re.search(pattern, context):
                        xpath_patterns_found.append(pattern)
                
                for source in USER_INPUT_SOURCES:
                    if re.search(source, context):
                        user_input_found.append(source)
                
                # Check for string concatenation
                string_concat = re.search(r'[\'"]\s*\+|\+\s*[\'"]', context) is not None
                
                # Risk assessment
                risk = 'LOW'
                if user_input_found and (xpath_patterns_found or string_concat):
                    risk = 'HIGH'
                elif user_input_found or string_concat:
                    risk = 'MEDIUM'
                elif xpath_patterns_found:
                    risk = 'LOW'
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'xpath_patterns': xpath_patterns_found,
                    'user_input_sources': user_input_found,
                    'uses_concatenation': string_concat,
                    'evaluation_type': 'document.evaluate' if 'document.evaluate' in sink 
                                     else 'element.evaluate' if 'element.evaluate' in sink 
                                     else 'other'
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
        f.write("DOM-Based XPath Injection Vulnerability Report\n")
        f.write("=========================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nXPath Injection Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    f.write(f"Evaluation Type: {finding['evaluation_type']}\n")
                    f.write(f"Uses String Concatenation: {'Yes' if finding['uses_concatenation'] else 'No'}\n")
                    
                    if finding['xpath_patterns']:
                        f.write("XPath Patterns Found:\n")
                        for pattern in finding['xpath_patterns']:
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
        
        # Evaluation type statistics
        doc_eval_count = sum(1 for findings in results.values() 
                            for finding in findings if finding['evaluation_type'] == 'document.evaluate')
        elem_eval_count = sum(1 for findings in results.values() 
                             for finding in findings if finding['evaluation_type'] == 'element.evaluate')
        other_eval_count = sum(1 for findings in results.values() 
                              for finding in findings if finding['evaluation_type'] == 'other')
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")
        f.write(f"Medium Risk Vulnerabilities: {medium_risk}\n")
        f.write("\nEvaluation Types Breakdown:\n")
        f.write(f"document.evaluate: {doc_eval_count}\n")
        f.write(f"element.evaluate: {elem_eval_count}\n")
        f.write(f"Other evaluation methods: {other_eval_count}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based XPath Injection Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='xpath_injection_report.txt', 
                        help='Output file name (default: xpath_injection_report.txt)')
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