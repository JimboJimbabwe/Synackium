import argparse
import requests
import re

def modify_and_send_request(input_file, new_method):
    # Read the curl command from file
    with open(input_file, 'r') as f:
        curl_command = f.read()

    # Extract the URL
    url_pattern = r'\$\'(http.*?)\''
    url_match = re.search(url_pattern, curl_command)
    if url_match:
        url = url_match.group(1)
    else:
        raise ValueError("No URL found in curl command")

    # Extract headers
    headers = {}
    header_pattern = r'-H \$\'(.*?): (.*?)\''
    header_matches = re.finditer(header_pattern, curl_command)
    
    for match in header_matches:
        header_name = match.group(1)
        header_value = match.group(2)
        headers[header_name] = header_value

    # Extract cookies
    cookies = {}
    cookie_pattern = r'-b \$\'(.*?)\''
    cookie_match = re.search(cookie_pattern, curl_command)
    if cookie_match:
        cookie_str = cookie_match.group(1)
        cookie_pairs = cookie_str.split('; ')
        for pair in cookie_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                cookies[key] = value

    # Send request with new method
    try:
        response = requests.request(
            method=new_method.upper(),
            url=url,
            headers=headers,
            cookies=cookies,
            verify=False,
            allow_redirects=True
        )

        print(f"Status Code: {response.status_code}")
        print("\nResponse Headers:")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        print("\nResponse Body:")
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

def main():
    parser = argparse.ArgumentParser(description='Modify HTTP method in curl command')
    parser.add_argument('-f', '--file', required=True, help='Input file containing curl command')
    parser.add_argument('-X', '--method', required=True, help='New HTTP method (GET, POST, PUT, etc.)')
    
    args = parser.parse_args()
    modify_and_send_request(args.file, args.method)

if __name__ == '__main__':
    main()
