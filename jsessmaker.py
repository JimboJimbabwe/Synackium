import base64
import argparse
import random
import time
import struct
from datetime import datetime

class JSESSIONIDHandler:
    @staticmethod
    def generate_jsessionid(seed=None, jvm_route=None):
        """Generate a JSESSIONID using an optional seed word and JVM route"""
        if seed:
            random.seed(hash(seed))
            
        timestamp = int(time.time() * 1000)
        random_bits = random.getrandbits(64)
        
        binary = struct.pack('>QQ', timestamp, random_bits)
        session_id = base64.b64encode(binary).decode('ascii')
        
        if jvm_route:
            session_id = f"{session_id}.{jvm_route}"
            
        return session_id

    @staticmethod
    def decode_jsessionid(jsessionid):
        try:
            base_id = jsessionid.split('.')[0]
            jvm_route = jsessionid.split('.')[1] if '.' in jsessionid else None
            
            padding_needed = len(base_id) % 4
            if padding_needed:
                base_id += "=" * (4 - padding_needed)
            
            binary = base64.b64decode(base_id)
            
            if len(binary) >= 16:
                timestamp, random_bits = struct.unpack('>QQ', binary[:16])
                dt = datetime.fromtimestamp(timestamp / 1000)
                
                return {
                    'timestamp': dt.isoformat(),
                    'random': hex(random_bits),
                    'jvm_route': jvm_route,
                    'raw_binary_length': len(binary)
                }
            else:
                return {
                    'error': 'Invalid JSESSIONID length',
                    'raw_binary_length': len(binary)
                }
                
        except Exception as e:
            return {
                'error': f'Failed to decode: {str(e)}',
                'raw_content': jsessionid
            }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='JSESSIONID Generator and Decoder')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--generate', metavar='SEED', nargs='?', const=None, 
                      help='Generate a new JSESSIONID with optional seed word')
    group.add_argument('--decode', metavar='JSESSIONID', help='Decode a JSESSIONID')
    parser.add_argument('--jvm-route', help='Optional JVM route for generation')
    
    args = parser.parse_args()
    handler = JSESSIONIDHandler()
    
    if args.generate is not None or args.generate == None:
        jsessionid = handler.generate_jsessionid(args.generate, args.jvm_route)
        print(f"Generated JSESSIONID: {jsessionid}")
        
    elif args.decode:
        result = handler.decode_jsessionid(args.decode)
        print("\nJSESSIONID Analysis:")
        for key, value in result.items():
            print(f"{key}: {value}")

# Example usage:
# Generate random: python jsessionid_tool.py --generate
# Generate with seed: python jsessionid_tool.py --generate myseed
# Generate with JVM route: python jsessionid_tool.py --generate --jvm-route node01
# Generate with both: python jsessionid_tool.py --generate myseed --jvm-route node01
# Decode: python jsessionid_tool.py --decode "ABC123.node01"
