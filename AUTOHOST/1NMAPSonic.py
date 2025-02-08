#!/usr/bin/env python3
import json
import subprocess
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

class NmapIPBankBuilder:
    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.ipbank_data: Dict = {}
        self.timing_template = "T4"  # Can be adjusted to T3 if needed
        
    def save_ipbank(self):
        """Save the current state of IPBank."""
        with open("IPBank.json", 'w') as f:
            json.dump(self.ipbank_data, f, indent=2)
        print("Saved IPBank.json")

    def load_ipbank(self):
        """Load existing IPBank if it exists."""
        try:
            with open("IPBank.json", 'r') as f:
                self.ipbank_data = json.load(f)
            print("Loaded existing IPBank.json")
        except FileNotFoundError:
            print("No existing IPBank.json found, creating new")

    def run_dns_resolution(self):
        """Phase 1: DNS Resolution scan."""
        print("\nPhase 1: DNS Resolution Scan")
        
        # Run nmap DNS resolution scan
        try:
            result = subprocess.run([
                'nmap', 
                '-sL',  # List scan - simply list targets to scan
                '-n',   # No DNS resolution
                '-oX', 'dns_scan.xml',  # Output to XML
                '-iL', str(self.input_file)  # Input from file
            ], capture_output=True, text=True, check=True)
            
            # Parse the XML output
            tree = ET.parse('dns_scan.xml')
            root = tree.getroot()
            
            # Process each host
            for host in root.findall('.//host'):
                ip = host.find('.//address[@addrtype="ipv4"]').get('addr')
                hostname_elem = host.find('.//hostname')
                
                self.ipbank_data[ip] = {
                    "Value": ip,
                    "ResolvedBoolean": hostname_elem is not None,
                    "ResolvedDomain": hostname_elem.get('name') if hostname_elem is not None else None,
                    "Ports": [],
                    "Service": [],
                    "Endpoints": [],
                    "PotentialPorts": []
                }
            
            print(f"Processed DNS resolution for {len(self.ipbank_data)} IPs")
            self.save_ipbank()
            
        except subprocess.CalledProcessError as e:
            print(f"Error during DNS resolution scan: {e}")
            sys.exit(1)

    def run_port_discovery(self):
        """Phase 2: Port discovery with -Pn scan."""
        print("\nPhase 2: Port Discovery Scan")
        
        for ip in self.ipbank_data.keys():
            print(f"Scanning ports for {ip}")
            try:
                # Run nmap port scan
                result = subprocess.run([
                    'nmap',
                    '-Pn',  # Treat all hosts as online
                    '-p-',  # Scan all ports
                    '-oX', f'portscan_{ip}.xml',  # Output to XML
                    ip
                ], capture_output=True, text=True, check=True)
                
                # Parse the XML output
                tree = ET.parse(f'portscan_{ip}.xml')
                root = tree.getroot()
                
                # Process ports
                ports = []
                for port in root.findall('.//port[@state="open"]'):
                    port_num = int(port.get('portid'))
                    ports.append(port_num)
                
                # Update IPBank entry
                self.ipbank_data[ip]["Ports"] = ports
                print(f"Found {len(ports)} open ports")
                
            except subprocess.CalledProcessError as e:
                print(f"Error scanning ports for {ip}: {e}")
                continue
            
        self.save_ipbank()

    def run_service_detection(self):
        """Phase 3: Service detection scan for discovered ports."""
        print("\nPhase 3: Service Detection Scan")
        
        for ip, data in self.ipbank_data.items():
            if not data["Ports"]:
                print(f"Skipping {ip} - no open ports")
                continue
                
            ports_str = ','.join(map(str, data["Ports"]))
            print(f"Detecting services for {ip} on ports {ports_str}")
            
            try:
                # Run nmap service detection
                result = subprocess.run([
                    'nmap',
                    '-sV',  # Service version detection
                    f'-{self.timing_template}',  # Timing template
                    '-p', ports_str,  # Specific ports
                    '-oX', f'services_{ip}.xml',  # Output to XML
                    ip
                ], capture_output=True, text=True, check=True)
                
                # Parse the XML output
                tree = ET.parse(f'services_{ip}.xml')
                root = tree.getroot()
                
                # Process services
                services = []
                for port in root.findall('.//port[@state="open"]'):
                    port_num = int(port.get('portid'))
                    service = port.find('service')
                    if service is not None:
                        services.append({
                            "port": port_num,
                            "service": service.get('name'),
                            "product": service.get('product', ''),
                            "version": service.get('version', '')
                        })
                
                # Update IPBank entry
                self.ipbank_data[ip]["Service"] = services
                print(f"Detected {len(services)} services")
                
            except subprocess.CalledProcessError as e:
                print(f"Error detecting services for {ip}: {e}")
                continue
            
        self.save_ipbank()

def main():
    if len(sys.argv) != 2:
        print("Usage: ./nmap_ipbank_builder.py <input_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    builder = NmapIPBankBuilder(input_file)
    builder.load_ipbank()
    
    # Run each phase
    builder.run_dns_resolution()
    builder.run_port_discovery()
    builder.run_service_detection()
    
    print("\nIPBank building complete!")

if __name__ == "__main__":
    main()
