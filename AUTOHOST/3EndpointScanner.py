#!/usr/bin/env python3
import json
import asyncio
import aiohttp
import glob
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import sys
import time

class EndpointScanner:
    def __init__(self, ipbank_path: Path, services_dir: Path):
        self.ipbank_path = ipbank_path
        self.services_dir = services_dir
        self.ipbank_data: Dict = {}
        self.service_definitions: Dict = {}  # Service name -> List of definitions with ports
        self.total_endpoints = 0
        self.scan_delay = 0.5  # Delay between requests in seconds
        
    async def load_files(self):
        """Load IPBank.json and all service definition files."""
        try:
            # Load IPBank
            with open(self.ipbank_path, 'r') as f:
                self.ipbank_data = json.load(f)
            print(f"Loaded IPBank.json with {len(self.ipbank_data)} entries")
            
            # Load all service definition files
            service_files = glob.glob(str(self.services_dir / "*.json"))
            for service_file in service_files:
                with open(service_file, 'r') as f:
                    service_data = json.load(f)
                    for port_info in service_data.get("Ports", []):
                        for service_def in port_info.get("PotentialServices", []):
                            service_name = service_def["Service"].lower()
                            if service_name not in self.service_definitions:
                                self.service_definitions[service_name] = []
                            # Add port to the service definition
                            service_def["Port"] = port_info["Port"]
                            self.service_definitions[service_name].append(service_def)
            
            print(f"Loaded service definitions from {len(service_files)} files")
            
        except FileNotFoundError as e:
            print(f"Error: Required file not found - {e.filename}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in input files - {e}")
            sys.exit(1)

    def find_service_definition(self, service_name: str) -> Optional[Tuple[int, Dict]]:
        """Find matching service definition and its port."""
        service_name_lower = service_name.lower()
        for name, definitions in self.service_definitions.items():
            if name in service_name_lower:
                for definition in definitions:
                    return definition["Port"], definition
        return None

    def save_ipbank(self):
        """Save the updated IPBank.json file."""
        with open(self.ipbank_path, 'w') as f:
            json.dump(self.ipbank_data, f, indent=2)
        print("\nSaved updated IPBank.json")

    def count_total_endpoints(self) -> int:
        """Count total endpoints to be scanned based on identified services."""
        total = 0
        for ip_data in self.ipbank_data.values():
            for service in ip_data.get("Service", []):
                service_name = service["service"]
                service_match = self.find_service_definition(service_name)
                
                if service_match:
                    _, service_def = service_match
                    total += len(service_def.get("DefaultEndpoints", []))
                    total += len(service_def.get("CommonEndpoints", []))
                    total += len(service_def.get("UndesirableEndpoints", []))
        return total

    async def test_endpoint(self, session: aiohttp.ClientSession, ip: str, port: int, endpoint: str, is_ssl: bool = False) -> bool:
        """Test a single endpoint and return True if it returns 200 OK."""
        protocol = "https" if is_ssl else "http"
        url = f"{protocol}://{ip}:{port}{endpoint}"
        print(f"Testing: {url}")
        
        try:
            async with session.get(url, ssl=False, timeout=5) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def scan_endpoints(self, ip: str, port: int, endpoints: List[str], endpoint_type: str, 
                           session: aiohttp.ClientSession, is_ssl: bool = False) -> List[str]:
        """Scan a list of endpoints and return successful ones."""
        successful_endpoints = []
        print(f"\nScanning {endpoint_type} endpoints for {ip}:{port}")
        
        for endpoint in endpoints:
            if await self.test_endpoint(session, ip, port, endpoint, is_ssl):
                full_endpoint = f"{ip}:{port}{endpoint}"
                successful_endpoints.append(full_endpoint)
                print(f"Found accessible endpoint: {full_endpoint}")
            await asyncio.sleep(self.scan_delay)
            
        return successful_endpoints

    async def process_service(self, ip: str, service: Dict, session: aiohttp.ClientSession):
        """Process a single service for an IP."""
        service_name = service["service"]
        service_match = self.find_service_definition(service_name)
        
        if service_match:
            port, service_def = service_match
            is_ssl = port in [443, 8443] or "ssl" in service_name.lower()
            
            print(f"\nProcessing {service_def['Service']} on {ip}:{port}")
            successful_endpoints = []
            
            # Test Default Endpoints
            default_endpoints = service_def.get("DefaultEndpoints", [])
            successful_endpoints.extend(
                await self.scan_endpoints(ip, port, default_endpoints, "Default", session, is_ssl)
            )
            
            # Test Common Endpoints
            common_endpoints = service_def.get("CommonEndpoints", [])
            successful_endpoints.extend(
                await self.scan_endpoints(ip, port, common_endpoints, "Common", session, is_ssl)
            )
            
            # Test Undesirable Endpoints
            undesirable_endpoints = service_def.get("UndesirableEndpoints", [])
            successful_endpoints.extend(
                await self.scan_endpoints(ip, port, undesirable_endpoints, "Undesirable", session, is_ssl)
            )
            
            return successful_endpoints
        return []

    async def process_ip(self, ip: str, data: Dict):
        """Process all services for a single IP."""
        if "Service" not in data:
            return
            
        if "Endpoints" not in data:
            data["Endpoints"] = []
            
        async with aiohttp.ClientSession() as session:
            for service in data["Service"]:
                endpoints = await self.process_service(ip, service, session)
                data["Endpoints"].extend(endpoints)
                
        # Remove duplicates while preserving order
        data["Endpoints"] = list(dict.fromkeys(data["Endpoints"]))

    async def process_all_ips(self):
        """Process all IPs in the IPBank."""
        self.total_endpoints = self.count_total_endpoints()
        print(f"\nTotal endpoints to scan: {self.total_endpoints}")
        
        for ip, data in self.ipbank_data.items():
            print(f"\nProcessing {ip}...")
            await self.process_ip(ip, data)

async def main():
    if len(sys.argv) != 3:
        print("Usage: ./endpoint_scanner.py <ipbank.json> <services_directory>")
        sys.exit(1)
    
    ipbank_path = Path(sys.argv[1])
    services_dir = Path(sys.argv[2])
    
    if not ipbank_path.exists():
        print(f"Error: {ipbank_path} not found")
        sys.exit(1)
    
    if not services_dir.exists() or not services_dir.is_dir():
        print(f"Error: {services_dir} is not a valid directory")
        sys.exit(1)
    
    print("Starting endpoint scanning...")
    
    scanner = EndpointScanner(ipbank_path, services_dir)
    await scanner.load_files()
    
    start_time = time.time()
    await scanner.process_all_ips()
    duration = time.time() - start_time
    
    scanner.save_ipbank()
    print(f"\nEndpoint scanning complete!")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total endpoints scanned: {scanner.total_endpoints}")

if __name__ == "__main__":
    asyncio.run(main())
