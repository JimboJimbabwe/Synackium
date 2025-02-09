#!/usr/bin/env python3
import json
import socket
import glob
import binascii
import re
from pathlib import Path
from typing import Dict, List, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys
import time

class ServiceProbeTester:
    def __init__(self, ipbank_path: Path, probe_dir: Path):
        self.ipbank_path = ipbank_path
        self.probe_dir = probe_dir
        self.ipbank_data: Dict = {}
        self.service_probes: Dict[int, List] = {}  # Port -> List of probes
        self.timeout = 5  # Socket timeout in seconds
        
    def load_ipbank(self):
        """Load the IPBank.json file."""
        try:
            with open(self.ipbank_path, 'r') as f:
                self.ipbank_data = json.load(f)
            print(f"Loaded IPBank.json with {len(self.ipbank_data)} entries")
        except FileNotFoundError:
            print("Error: IPBank.json not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in IPBank.json")
            sys.exit(1)

    def load_probe_files(self):
        """Load all probe JSON files from the specified directory."""
        probe_files = glob.glob(str(self.probe_dir / "*.json"))
        if not probe_files:
            print("Error: No probe definition files found")
            sys.exit(1)

        for probe_file in probe_files:
            try:
                with open(probe_file, 'r') as f:
                    probe_data = json.load(f)
                    
                    # Index probes by port for quick lookup
                    for service in probe_data.get("ServiceProbes", []):
                        port = service.get("DefaultPort")
                        if port:
                            if port not in self.service_probes:
                                self.service_probes[port] = []
                            self.service_probes[port].append(service)
                            
                print(f"Loaded probes from {probe_file}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading {probe_file}: {str(e)}")
                continue

    def save_ipbank(self):
        """Save the updated IPBank.json file."""
        with open(self.ipbank_path, 'w') as f:
            json.dump(self.ipbank_data, f, indent=2)
        print("Saved updated IPBank.json")

    def decode_hex_string(self, hex_string: str) -> bytes:
        """Convert a hex string to bytes for binary protocols."""
        return binascii.unhexlify(hex_string)

    async def test_probe(self, ip: str, port: int, probe: Dict) -> Optional[str]:
        """Test a single probe against an IP:port combination."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            print(f"Testing {ip}:{port} - {probe['Description']}")
            
            try:
                await asyncio.get_event_loop().sock_connect(sock, (ip, port))
                
                # Prepare and send probe data
                if isinstance(probe["Send"], dict) and "HexString" in probe["Send"]:
                    probe_data = self.decode_hex_string(probe["Send"]["HexString"])
                else:
                    probe_data = probe["Send"].encode()
                
                print(f"Sending: {probe['Send']}")
                await asyncio.get_event_loop().sock_sendall(sock, probe_data)
                
                # Receive response
                response = await asyncio.get_event_loop().sock_recv(sock, 2048)
                
                # Check against expected responses
                for expected in probe["ExpectedResponses"]:
                    pattern = expected["Pattern"]
                    
                    # Handle binary patterns
                    if pattern.startswith("\\x"):
                        pattern_bytes = pattern.encode().decode('unicode-escape').encode()
                        if pattern_bytes in response:
                            return expected["Indicates"]
                    else:
                        # Use regex for text patterns
                        if re.search(pattern, response.decode('utf-8', errors='ignore')):
                            return expected["Indicates"]
                            
            finally:
                sock.close()
                
        except (socket.timeout, socket.error) as e:
            print(f"Error testing {ip}:{port} - {str(e)}")
            return None
            
        return None

    async def process_ip(self, ip: str, data: Dict):
        """Process all ports for a single IP address."""
        if not data.get("Ports"):
            print(f"No ports found for {ip}")
            return
            
        # Initialize Service array if it doesn't exist
        if "Service" not in data:
            data["Service"] = []
            
        # Track ports we've already processed
        processed_ports = set()
        
        for port in data["Ports"]:
            if port in processed_ports:
                continue
                
            processed_ports.add(port)
            
            if port in self.service_probes:
                print(f"\nChecking port {port} on {ip}")
                
                for service_def in self.service_probes[port]:
                    service_name = service_def["Service"]
                    
                    for probe in service_def["Probes"]:
                        print(f"Testing for {service_name}, {probe['Description']}")
                        result = await self.test_probe(ip, port, probe)
                        
                        if result:
                            service_entry = {
                                "port": port,
                                "service": result
                            }
                            data["Service"].append(service_entry)
                            print(f"Identified service: {result}")
                            break  # Move to next service definition
                    
                    # Add a small delay between services
                    await asyncio.sleep(0.5)

    async def process_all_ips(self):
        """Process all IPs in the IPBank."""
        for ip, data in self.ipbank_data.items():
            print(f"\nProcessing {ip}...")
            await self.process_ip(ip, data)
            # Add a small delay between IPs
            await asyncio.sleep(1)

async def main():
    if len(sys.argv) != 3:
        print("Usage: ./service_probe_tester.py <ipbank.json> <probe_directory>")
        sys.exit(1)
    
    ipbank_path = Path(sys.argv[1])
    probe_dir = Path(sys.argv[2])
    
    if not ipbank_path.exists():
        print(f"Error: {ipbank_path} not found")
        sys.exit(1)
    
    if not probe_dir.exists() or not probe_dir.is_dir():
        print(f"Error: {probe_dir} is not a valid directory")
        sys.exit(1)
    
    print("Starting service probe testing...")
    
    tester = ServiceProbeTester(ipbank_path, probe_dir)
    tester.load_ipbank()
    tester.load_probe_files()
    
    start_time = time.time()
    await tester.process_all_ips()
    duration = time.time() - start_time
    
    tester.save_ipbank()
    print(f"\nService probe testing complete! Duration: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
