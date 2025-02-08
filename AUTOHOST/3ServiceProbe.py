#!/usr/bin/env python3
import json
import socket
import glob
import re
import binascii
from pathlib import Path
from typing import Dict, List, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import struct

class ServiceProber:
    def __init__(self, ipbank_path: Path, probe_paths: List[Path]):
        self.ipbank_path = ipbank_path
        self.probe_paths = probe_paths
        self.ipbank_data: Dict = {}
        self.service_probes: Dict[int, List] = {}  # Port -> List of probe configs
        self.timeout = 5  # Socket timeout in seconds
        self.probe_delay = 10  # Delay between probes in seconds
        self.last_probe_time = 0  # Track time of last probe
        
    def load_files(self):
        """Load IPBank.json and all probe definition files."""
        try:
            # Load IPBank
            with open(self.ipbank_path, 'r') as f:
                self.ipbank_data = json.load(f)
            print(f"Loaded IPBank.json with {len(self.ipbank_data)} entries")
            
            # Load all probe definition files
            for probe_path in self.probe_paths:
                with open(probe_path, 'r') as f:
                    probe_data = json.load(f)
                    # Index probes by port for quick lookup
                    for service in probe_data["ServiceProbes"]:
                        port = service["DefaultPort"]
                        if port not in self.service_probes:
                            self.service_probes[port] = []
                        self.service_probes[port].append(service)
                print(f"Loaded probe definitions from {probe_path}")
                
        except FileNotFoundError as e:
            print(f"Error: Required file not found - {e.filename}")
            exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in input files - {e}")
            exit(1)

    def save_ipbank(self):
        """Save the updated IPBank.json file."""
        with open(self.ipbank_path, 'w') as f:
            json.dump(self.ipbank_data, f, indent=2)
        print("Saved updated IPBank.json")

    def decode_hex_string(self, hex_string: str) -> bytes:
        """Convert a hex string to bytes for binary protocols."""
        return binascii.unhexlify(hex_string)

    async def wait_between_probes(self):
        """Ensure we wait the required time between probes."""
        current_time = asyncio.get_event_loop().time()
        time_since_last_probe = current_time - self.last_probe_time
        
        if time_since_last_probe < self.probe_delay:
            wait_time = self.probe_delay - time_since_last_probe
            print(f"Waiting {wait_time:.1f} seconds before next probe...")
            await asyncio.sleep(wait_time)
        
        self.last_probe_time = asyncio.get_event_loop().time()

    async def probe_service(self, ip: str, port: int, probe_config: Dict) -> Optional[str]:
        """
        Probe a specific service on an IP:port combination.
        Returns the service identification if successful, None otherwise.
        """
        # Wait required time before starting new probe
        await self.wait_between_probes()
        
        try:
            for probe in probe_config["Probes"]:
                print(f"Sending probe to {ip}:{port} - {probe['Description']}")
                
                # Create a new socket for each probe
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                
                try:
                    # Connect to the target
                    await asyncio.get_event_loop().sock_connect(sock, (ip, port))
                    
                    # Prepare and send probe data
                    if isinstance(probe["Send"], dict) and "HexString" in probe["Send"]:
                        probe_data = self.decode_hex_string(probe["Send"]["HexString"])
                    else:
                        probe_data = probe["Send"].encode()
                    
                    await asyncio.get_event_loop().sock_sendall(sock, probe_data)
                    
                    # Receive response
                    response = await asyncio.get_event_loop().sock_recv(sock, 1024)
                    
                    # Check against expected responses
                    for expected in probe["ExpectedResponses"]:
                        pattern = expected["Pattern"]
                        
                        # Handle binary patterns
                        if pattern.startswith("\\x"):
                            # Convert pattern to bytes and use direct comparison
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
            print(f"Error probing {ip}:{port} - {str(e)}")
            return None
            
        return None

    async def process_ip(self, ip: str, data: Dict):
        """Process a single IP address entry from IPBank."""
        if not data.get("PotentialPorts"):
            return
            
        for port_info in data["PotentialPorts"]:
            port = port_info["port"]
            
            if port in self.service_probes:
                print(f"\nProbing {ip}:{port}")
                
                # Initialize service array if it doesn't exist
                if "Service" not in data:
                    data["Service"] = []
                
                # Try each probe configuration for this port
                for probe_config in self.service_probes[port]:
                    service_result = await self.probe_service(ip, port, probe_config)
                    
                    if service_result:
                        # Add service identification to the Service array
                        service_entry = {
                            "port": port,
                            "service": service_result
                        }
                        data["Service"].append(service_entry)
                        print(f"Identified service on {ip}:{port} - {service_result}")
                        break
                else:
                    # No response for any probe
                    service_entry = {
                        "port": port,
                        "service": "No Response"
                    }
                    data["Service"].append(service_entry)
                    print(f"No response from {ip}:{port}")

    async def process_all_ips(self):
        """Process all IPs in the IPBank."""
        # Process IPs sequentially to maintain proper probe delays
        for ip, data in self.ipbank_data.items():
            await self.process_ip(ip, data)

async def main():
    # Get all probe definition files
    probe_files = glob.glob("serviceprobes*.json")
    if not probe_files:
        print("Error: No service probe definition files found")
        exit(1)
    
    probe_paths = [Path(f) for f in probe_files]
    ipbank_path = Path("IPBank.json")
    
    print("Starting service detection process...")
    print("Note: Waiting 10 seconds between each probe for rate limiting")
    
    # Initialize and run the prober
    prober = ServiceProber(ipbank_path, probe_paths)
    prober.load_files()
    
    # Process all IPs
    await prober.process_all_ips()
    
    # Save the results
    prober.save_ipbank()
    
    print("\nService detection complete!")

if __name__ == "__main__":
    asyncio.run(main())
