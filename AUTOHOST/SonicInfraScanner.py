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
import time

class ServiceProber:
    def __init__(self, ipbank_path: Path, probe_paths: List[Path]):
        self.ipbank_path = ipbank_path
        self.probe_paths = probe_paths
        self.ipbank_data: Dict = {}
        self.service_probes: Dict[int, List] = {}
        self.timeout = 2  # Reduced socket timeout for faster processing
        self.probe_delay = 0.8  # Short delay between probes
        self.last_probe_time = 0
        self.semaphore = asyncio.Semaphore(50)  # Limit concurrent connections
        
    def load_files(self):
        """Load IPBank.json and all probe definition files."""
        try:
            with open(self.ipbank_path, 'r') as f:
                self.ipbank_data = json.load(f)
            print(f"Loaded IPBank.json with {len(self.ipbank_data)} entries")
            
            for probe_path in self.probe_paths:
                with open(probe_path, 'r') as f:
                    probe_data = json.load(f)
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

    def decode_hex_string(self, hex_string: str) -> bytes:
        """Convert a hex string to bytes for binary protocols."""
        return binascii.unhexlify(hex_string)

    async def rate_limit(self):
        """Basic rate limiting between probes."""
        current_time = time.time()
        time_since_last = current_time - self.last_probe_time
        if time_since_last < self.probe_delay:
            await asyncio.sleep(self.probe_delay - time_since_last)
        self.last_probe_time = time.time()

    async def probe_service(self, ip: str, port: int, probe_config: Dict) -> Optional[str]:
        """Probe a specific service on an IP:port combination."""
        async with self.semaphore:  # Limit concurrent connections
            await self.rate_limit()
            
            try:
                for probe in probe_config["Probes"]:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.timeout)
                    
                    try:
                        await asyncio.get_event_loop().sock_connect(sock, (ip, port))
                        
                        if isinstance(probe["Send"], dict) and "HexString" in probe["Send"]:
                            probe_data = self.decode_hex_string(probe["Send"]["HexString"])
                        else:
                            probe_data = probe["Send"].encode()
                        
                        await asyncio.get_event_loop().sock_sendall(sock, probe_data)
                        response = await asyncio.get_event_loop().sock_recv(sock, 1024)
                        
                        for expected in probe["ExpectedResponses"]:
                            pattern = expected["Pattern"]
                            
                            if pattern.startswith("\\x"):
                                pattern_bytes = pattern.encode().decode('unicode-escape').encode()
                                if pattern_bytes in response:
                                    return expected["Indicates"]
                            else:
                                if re.search(pattern, response.decode('utf-8', errors='ignore')):
                                    return expected["Indicates"]
                    
                    except (socket.timeout, socket.error):
                        continue
                    finally:
                        sock.close()
                        
            except Exception as e:
                print(f"Error probing {ip}:{port} - {str(e)}")
                
            return None

    async def process_ports(self, ip: str, data: Dict):
        """Process all ports for a single IP."""
        if not data.get("PotentialPorts"):
            return []

        tasks = []
        for port_info in data["PotentialPorts"]:
            port = port_info["port"]
            if port in self.service_probes:
                for probe_config in self.service_probes[port]:
                    tasks.append(self.probe_service(ip, port, probe_config))

        results = await asyncio.gather(*tasks)
        return [(port_info["port"], result) for port_info, result in zip(data["PotentialPorts"], results) if result]

    async def process_ip(self, ip: str, data: Dict):
        """Process a single IP address entry."""
        if not data.get("PotentialPorts"):
            return

        print(f"Scanning {ip}...")
        results = await self.process_ports(ip, data)
        
        if "Service" not in data:
            data["Service"] = []
            
        for port, service in results:
            if service:
                data["Service"].append({
                    "port": port,
                    "service": service
                })
            else:
                data["Service"].append({
                    "port": port,
                    "service": "No Response"
                })

    async def process_all_ips(self):
        """Process all IPs in parallel with rate limiting."""
        tasks = []
        for ip, data in self.ipbank_data.items():
            tasks.append(self.process_ip(ip, data))
        
        await asyncio.gather(*tasks)

async def main():
    probe_files = glob.glob("serviceprobes*.json")
    if not probe_files:
        print("Error: No service probe definition files found")
        exit(1)
    
    probe_paths = [Path(f) for f in probe_files]
    ipbank_path = Path("IPBank.json")
    
    print("Starting high-speed service detection...")
    
    start_time = time.time()
    prober = ServiceProber(ipbank_path, probe_paths)
    prober.load_files()
    
    await prober.process_all_ips()
    
    prober.save_ipbank()
    
    duration = time.time() - start_time
    print(f"\nService detection complete! Duration: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
