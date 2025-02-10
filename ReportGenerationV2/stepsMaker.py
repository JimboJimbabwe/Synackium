import json
import re
import argparse
from pathlib import Path

def format_steps(json_data):
    """
    Format steps data from JSON into a specific markdown format.
    
    Args:
        json_data (list): List of step dictionaries from the JSON file
    
    Returns:
        str: Formatted string with steps and references
    """
    output = ["###### Steps Taken:"]
    
    # Handle references before steps if they exist in any step
    initial_references = []
    for step in json_data:
        if step['ReferenceImages'] and len(step['ReferenceImages']) > 0:
            for image_path in step['ReferenceImages']:
                match = re.search(r'\\sc\d+reference\d+\.png', image_path)
                if match:
                    ref = match.group().lstrip('\\')
                    initial_references.append(f"*Reference: {ref}")
    
    # Add initial references if they exist
    if initial_references:
        output.extend(initial_references)
        output.append("")  # Add blank line after initial references
    
    # Process steps
    for step in json_data:
        # Add step number and action
        output.append(f"{step['Step']}. {step['Action']}")
        
        # Process reference images for this step
        if step['ReferenceImages'] and len(step['ReferenceImages']) > 0:
            for image_path in step['ReferenceImages']:
                match = re.search(r'\\sc\d+reference\d+\.png', image_path)
                if match:
                    ref = match.group().lstrip('\\')
                    output.append(f"*Reference: {ref}")
        
        # Add blank line between steps
        output.append("")
    
    return "\n".join(output)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Format JSON steps data into markdown')
    parser.add_argument('json_file', type=str, help='Path to the JSON file')
    parser.add_argument('--output', '-o', type=str, help='Output file path (optional)')
    
    args = parser.parse_args()
    
    try:
        # Read JSON file
        with open(args.json_file, 'r') as f:
            json_data = json.load(f)
        
        # Format the steps
        formatted_output = format_steps(json_data)
        
        # Handle output
        if args.output:
            # Write to output file
            with open(args.output, 'w') as f:
                f.write(formatted_output)
            print(f"Output written to {args.output}")
        else:
            # Print to console
            print(formatted_output)
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.json_file}'")
    except json.JSONDecodeError:
        print(f"Error: '{args.json_file}' is not a valid JSON file")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
