# dom_sql_injection_scanner.py
import os
import re
import argparse
from pathlib import Path

SQL_SINKS = [
    r'executeSql\s*\(',
    r'openDatabase\s*\(',
    r'transaction\s*\(',
    r'query\s*\(',
    r'\.run\s*\(',
    r'\.exec\s*\(',
    r'\.execute\s*\(',
    r'indexedDB\.open\s*\(',
    r'createObjectStore\s*\(',
    r'\.put\s*\(',
    r'\.add\s*\(',
    r'\.delete\s*\(',
    r'\.get\s*\('
]

SQL_KEYWORDS = [
    r'SELECT\s+.*?\s+FROM',
    r'INSERT\s+INTO',
    r'UPDATE\s+.*?\s+SET',
    r'DELETE\s+FROM',
    r'DROP\s+TABLE',
    r'CREATE\s+TABLE',
    r'ALTER\s+TABLE',
    r'UNION\s+SELECT',
    r'JOIN\s+',
    r'WHERE\s+'
]

DANGEROUS_PATTERNS = [
    r'\+\s*[\'"].*?[\'"]',           # String concatenation
    r'\$\{.*?\}',                    # Template literals
    r'`.*?`',                        # Template strings
    r'\?\s*\+',                      # Parameter concatenation
    r'%\s*\+',                       # Format string concatenation
    r'\'.*?\'.*?\'',                 # Multiple string literals
    r'".*?".*?"'                     # Multiple double quotes
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
    r'localStorage',
    r'sessionStorage'
]

def analyze_js_file(file_path):
    findings = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        for sink in SQL_SINKS:
            matches = re.finditer(sink, content)
            for match in matches:
                start = max(0, match.start() - 100)  # Larger context for SQL queries
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                
                line_number = content.count('\n', 0, match.start()) + 1
                
                # Check for SQL keywords, dangerous patterns, and user input
                sql_keywords_found = []
                dangerous_patterns_found = []
                user_input_found = []
                
                for keyword in SQL_KEYWORDS:
                    if re.search(keyword, context, re.IGNORECASE):
                        sql_keywords_found.append(keyword)
                
                for pattern in DANGEROUS_PATTERNS:
                    if re.search(pattern, context):
                        dangerous_patterns_found.append(pattern)
                
                for source in USER_INPUT_SOURCES:
                    if re.search(source, context):
                        user_input_found.append(source)
                
                # Risk assessment
                risk = 'LOW'
                if sql_keywords_found and (dangerous_patterns_found or user_input_found):
                    risk = 'HIGH'
                elif sql_keywords_found or dangerous_patterns_found:
                    risk = 'MEDIUM'
                
                # Determine if parameterized query is used
                is_parameterized = '?' in context and not any(p in context for p in ['?+', '? +'])
                
                findings.append({
                    'sink': sink.replace('\\(', '').replace('\\s*', ' '),
                    'line': line_number,
                    'context': context,
                    'risk': risk,
                    'sql_keywords': sql_keywords_found,
                    'dangerous_patterns': dangerous_patterns_found,
                    'user_input_sources': user_input_found,
                    'is_parameterized': is_parameterized,
                    'database_type': 'WebSQL' if 'executeSql' in sink or 'openDatabase' in sink else 'IndexedDB'
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
        f.write("DOM-Based Client-Side SQL Injection Vulnerability Report\n")
        f.write("================================================\n\n")
        
        for file_path, findings in results.items():
            if findings:
                f.write(f"\nFile: {file_path}\n")
                f.write("-" * (len(file_path) + 6) + "\n")
                
                for finding in findings:
                    f.write(f"\nSQL Injection Sink: {finding['sink']}\n")
                    f.write(f"Line Number: {finding['line']}\n")
                    f.write(f"Risk Level: {finding['risk']}\n")
                    f.write(f"Database Type: {finding['database_type']}\n")
                    f.write(f"Uses Parameterized Query: {'Yes' if finding['is_parameterized'] else 'No'}\n")
                    
                    if finding['sql_keywords']:
                        f.write("SQL Keywords Found:\n")
                        for keyword in finding['sql_keywords']:
                            f.write(f"  - {keyword}\n")
                    
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
        
        # Database type statistics
        websql_count = sum(1 for findings in results.values() 
                          for finding in findings if finding['database_type'] == 'WebSQL')
        indexeddb_count = sum(1 for findings in results.values() 
                             for finding in findings if finding['database_type'] == 'IndexedDB')
        
        # Query type statistics
        parameterized_count = sum(1 for findings in results.values() 
                                 for finding in findings if finding['is_parameterized'])
        non_parameterized_count = sum(1 for findings in results.values() 
                                     for finding in findings if not finding['is_parameterized'])
        
        f.write("\nSummary Statistics\n")
        f.write("=================\n")
        f.write(f"Total Files Scanned: {total_files}\n")
        f.write(f"Total Vulnerabilities Found: {total_vulnerabilities}\n")
        f.write(f"High Risk Vulnerabilities: {high_risk}\n")
        f.write(f"Medium Risk Vulnerabilities: {medium_risk}\n")
        f.write("\nDatabase Types Breakdown:\n")
        f.write(f"WebSQL: {websql_count}\n")
        f.write(f"IndexedDB: {indexeddb_count}\n")
        f.write("\nQuery Types Breakdown:\n")
        f.write(f"Parameterized Queries: {parameterized_count}\n")
        f.write(f"Non-Parameterized Queries: {non_parameterized_count}\n")

def main():
    parser = argparse.ArgumentParser(description='DOM-Based Client-Side SQL Injection Scanner')
    parser.add_argument('-p', '--path', required=True, help='Directory path to scan')
    parser.add_argument('-o', '--output', default='sql_injection_report.txt', 
                        help='Output file name (default: sql_injection_report.txt)')
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