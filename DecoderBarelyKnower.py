import base64
import html
import urllib.parse
import json
import binascii
import codecs
import re
import zlib
from typing import Union, Optional
from itertools import cycle

class ExtendedDecoder:
    def __init__(self):
        self.morse_code_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9'
        }

    def decode_all(self, encoded_string: str) -> dict:
        """
        Attempts to decode a string using 30 different decoding methods.
        Returns a dictionary with results from all successful decoding attempts.
        """
        results = {}
        
        # Original 10 methods
        # 1. Base64 Decode
        try:
            decoded = base64.b64decode(encoded_string.encode()).decode()
            results['base64'] = decoded
        except:
            results['base64'] = None

        # 2. URL Decode
        try:
            results['url'] = urllib.parse.unquote(encoded_string)
        except:
            results['url'] = None

        # 3. HTML Entities
        try:
            results['html'] = html.unescape(encoded_string)
        except:
            results['html'] = None

        # 4. JSON String
        try:
            results['json'] = json.loads(encoded_string)
        except:
            results['json'] = None

        # 5. Hex to String
        try:
            hex_str = encoded_string.replace('0x', '')
            results['hex'] = bytes.fromhex(hex_str).decode('utf-8')
        except:
            results['hex'] = None

        # 6. ROT13
        try:
            results['rot13'] = codecs.decode(encoded_string, 'rot13')
        except:
            results['rot13'] = None

        # 7. Binary to String
        try:
            binary_str = encoded_string.replace(' ', '')
            if all(c in '01' for c in binary_str):
                n = int(binary_str, 2)
                results['binary'] = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big').decode()
        except:
            results['binary'] = None

        # 8. ASCII Character Codes
        try:
            ascii_nums = [int(x.strip()) for x in encoded_string.split(',')]
            results['ascii'] = ''.join(chr(x) for x in ascii_nums)
        except:
            results['ascii'] = None

        # 9. Unicode Escapes
        try:
            results['unicode_escape'] = encoded_string.encode().decode('unicode-escape')
        except:
            results['unicode_escape'] = None

        # 10. Morse Code
        try:
            morse_words = encoded_string.split(' / ')
            decoded_words = []
            for word in morse_words:
                decoded_chars = [self.morse_code_dict[char] for char in word.split()]
                decoded_words.append(''.join(decoded_chars))
            results['morse'] = ' '.join(decoded_words)
        except:
            results['morse'] = None

        # New methods (11-30)
        # 11. Base32 Decode
        try:
            results['base32'] = base64.b32decode(encoded_string).decode()
        except:
            results['base32'] = None

        # 12. Base85 Decode
        try:
            results['base85'] = base64.b85decode(encoded_string).decode()
        except:
            results['base85'] = None

        # 13. Quoted Printable
        try:
            results['quoted_printable'] = codecs.decode(encoded_string.encode(), 'quopri').decode()
        except:
            results['quoted_printable'] = None

        # 14. Octal to String
        try:
            octal_str = encoded_string.replace('\\', '')
            results['octal'] = ''.join(chr(int(octal_str[i:i+3], 8)) for i in range(0, len(octal_str), 3))
        except:
            results['octal'] = None

        # 15. Caesar Cipher (all shifts)
        try:
            shifts = []
            for shift in range(1, 26):
                decoded = ''.join(chr((ord(char) - ord('A' if char.isupper() else 'a') + shift) % 26 
                                + ord('A' if char.isupper() else 'a')) if char.isalpha() else char 
                                for char in encoded_string)
                shifts.append(f"Shift {shift}: {decoded}")
            results['caesar'] = shifts
        except:
            results['caesar'] = None

        # 16. Base58 (Bitcoin style)
        try:
            import base58
            results['base58'] = base58.b58decode(encoded_string).decode()
        except:
            results['base58'] = None

        # 17. Decimal UTF-16 Codes
        try:
            utf16_nums = [int(x.strip()) for x in encoded_string.split()]
            results['utf16'] = ''.join(chr(x) for x in utf16_nums)
        except:
            results['utf16'] = None

        # 18. Base64 URL Safe
        try:
            results['base64url'] = base64.urlsafe_b64decode(encoded_string).decode()
        except:
            results['base64url'] = None

        # 19. Atbash Cipher
        try:
            atbash = lambda c: chr(ord('Z') - (ord(c.upper()) - ord('A'))) if c.isalpha() else c
            results['atbash'] = ''.join(atbash(c) for c in encoded_string)
        except:
            results['atbash'] = None

        # 20. Unicode Code Points
        try:
            unicode_points = encoded_string.split('U+')[1:]
            results['unicode_points'] = ''.join(chr(int(point.strip(), 16)) for point in unicode_points)
        except:
            results['unicode_points'] = None

        # 21. Punycode (IDN)
        try:
            results['punycode'] = encoded_string.encode('ascii').decode('punycode')
        except:
            results['punycode'] = None

        # 22. Base16 (Hex)
        try:
            results['base16'] = base64.b16decode(encoded_string).decode()
        except:
            results['base16'] = None

        # 23. Vigenère Cipher (with common keys)
        try:
            common_keys = ['KEY', 'PASSWORD', 'SECRET', 'CIPHER']
            vigenere_results = []
            for key in common_keys:
                decoded = ''
                key_cycle = cycle(key)
                for char in encoded_string.upper():
                    if char.isalpha():
                        key_char = next(key_cycle)
                        decoded += chr((ord(char) - ord(key_char) + 26) % 26 + ord('A'))
                    else:
                        decoded += char
                vigenere_results.append(f"Key '{key}': {decoded}")
            results['vigenere'] = vigenere_results
        except:
            results['vigenere'] = None

        # 24. Reverse Text
        try:
            results['reverse'] = encoded_string[::-1]
        except:
            results['reverse'] = None

        # 25. Zlib Compressed
        try:
            compressed_data = encoded_string.encode('latin1')
            results['zlib'] = zlib.decompress(compressed_data).decode()
        except:
            results['zlib'] = None

        # 26. Base91
        try:
            from base91 import decode as b91decode
            results['base91'] = b91decode(encoded_string).decode()
        except:
            results['base91'] = None

        # 27. UUEncode
        try:
            results['uuencode'] = codecs.decode(encoded_string.encode(), 'uu').decode()
        except:
            results['uuencode'] = None

        # 28. XXEncode
        try:
            results['xxencode'] = codecs.decode(encoded_string.encode(), 'xx').decode()
        except:
            results['xxencode'] = None

        # 29. Decimal ASCII with different separators
        try:
            for separator in [',', ';', '|', ' ']:
                try:
                    nums = [int(x.strip()) for x in encoded_string.split(separator)]
                    results[f'ascii_{separator}'] = ''.join(chr(x) for x in nums)
                except:
                    continue
        except:
            results['ascii_separated'] = None

        # 30. JWT Decoder
        try:
            import jwt
            # Try to decode without verification
            results['jwt'] = jwt.decode(encoded_string, options={"verify_signature": False})
        except:
            results['jwt'] = None

        # Remove failed attempts
        return {k: v for k, v in results.items() if v is not None}

def test_decoder():
    decoder = ExtendedDecoder()
    
    # Test cases
    test_cases = {
        'base64': "SGVsbG8gV29ybGQ=",
        'url': "Hello%20World",
        'html': "&lt;Hello&gt;",
        'hex': "48656c6c6f20576f726c64",
        'base32': "JBSWY3DPEBLW64TMMQQQ====",
        'morse': ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
    }
    
    for encoding_type, test_string in test_cases.items():
        print(f"\nTesting {encoding_type}: {test_string}")
        results = decoder.decode_all(test_string)
        for method, result in results.items():
            print(f"{method}: {result}")

if __name__ == "__main__":
    test_decoder()
