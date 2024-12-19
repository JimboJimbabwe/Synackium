import tkinter as tk
from tkinter import ttk, scrolledtext
import base64
import html
import urllib.parse
import json
import binascii
import codecs
import re
from typing import Union, Optional
from itertools import cycle
from ttkthemes import ThemedTk


class DecoderGUI:
    def __init__(self):
        # Create themed root window
        self.root = ThemedTk(theme="arc")  # Modern theme
        self.root.title("Universal Decoder")
        self.root.geometry("800x600")

        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Input frame
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Input Text")
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Input text box
        self.input_text = scrolledtext.ScrolledText(self.input_frame, height=4)
        self.input_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Results frame with canvas and scrollbar
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Decoding Results")
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.results_frame)
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Grid canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind input changes to decoder
        self.input_text.bind('<KeyRelease>', self.on_input_change)

        # Store result labels
        self.result_labels = {}

        # Initialize decoder methods
        self.init_decoder_methods()

        # Create initial empty results
        self.create_result_labels()

    def init_decoder_methods(self):
        """Initialize all decoder methods with their friendly names"""
        self.decoder_methods = {
            'Base64': self.decode_base64,
            'URL': self.decode_url,
            'HTML': self.decode_html,
            'ROT13': self.decode_rot13,
            'Hex': self.decode_hex,
            'Binary': self.decode_binary,
            'ASCII': self.decode_ascii,
            'Base32': self.decode_base32,
            'Base85': self.decode_base85,
            'Morse Code': self.decode_morse,
            'Unicode Escape': self.decode_unicode_escape,
            'Reverse': self.decode_reverse,
            'Caesar Shift': self.decode_caesar,
            'Atbash': self.decode_atbash
        }

    def create_result_labels(self):
        """Create labels for all decoder methods"""
        for i, (method_name, _) in enumerate(self.decoder_methods.items()):
            # Frame for each result row
            frame = ttk.Frame(self.scrollable_frame)
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            frame.grid_columnconfigure(1, weight=1)

            # Method name label
            method_label = ttk.Label(frame, text=f"{method_name}:", width=15, anchor="e")
            method_label.grid(row=0, column=0, padx=(5, 10))

            # Result label
            result_label = ttk.Label(frame, text="", anchor="w")
            result_label.grid(row=0, column=1, sticky="ew")

            # Status label (✓ or ✗)
            status_label = ttk.Label(frame, text="", width=3)
            status_label.grid(row=0, column=2, padx=5)

            self.result_labels[method_name] = (result_label, status_label)

    def update_result(self, method_name: str, result: Union[str, None]):
        """Update the result and status for a given method"""
        result_label, status_label = self.result_labels[method_name]
        if result is not None:
            result_label.config(text=result[:100] + "..." if len(result) > 100 else result)
            status_label.config(text="✓", foreground="green")
        else:
            result_label.config(text="")
            status_label.config(text="✗", foreground="red")

    def on_input_change(self, event=None):
        """Handle input changes and update all results"""
        input_text = self.input_text.get("1.0", "end-1c").strip()
        if not input_text:
            for method_name in self.decoder_methods:
                self.update_result(method_name, None)
            return

        for method_name, decoder_func in self.decoder_methods.items():
            try:
                result = decoder_func(input_text)
                self.update_result(method_name, result)
            except:
                self.update_result(method_name, None)

    # Decoder methods
    def decode_base64(self, text: str) -> Optional[str]:
        try:
            return base64.b64decode(text.encode()).decode()
        except:
            return None

    def decode_url(self, text: str) -> Optional[str]:
        try:
            return urllib.parse.unquote(text)
        except:
            return None

    def decode_html(self, text: str) -> Optional[str]:
        try:
            return html.unescape(text)
        except:
            return None

    def decode_rot13(self, text: str) -> Optional[str]:
        try:
            return codecs.decode(text, 'rot13')
        except:
            return None

    def decode_hex(self, text: str) -> Optional[str]:
        try:
            hex_str = text.replace('0x', '')
            return bytes.fromhex(hex_str).decode('utf-8')
        except:
            return None

    def decode_binary(self, text: str) -> Optional[str]:
        try:
            binary_str = text.replace(' ', '')
            if all(c in '01' for c in binary_str):
                n = int(binary_str, 2)
                return n.to_bytes((n.bit_length() + 7) // 8, byteorder='big').decode()
            return None
        except:
            return None

    def decode_ascii(self, text: str) -> Optional[str]:
        try:
            ascii_nums = [int(x.strip()) for x in text.split(',')]
            return ''.join(chr(x) for x in ascii_nums)
        except:
            return None

    def decode_base32(self, text: str) -> Optional[str]:
        try:
            return base64.b32decode(text).decode()
        except:
            return None

    def decode_base85(self, text: str) -> Optional[str]:
        try:
            return base64.b85decode(text).decode()
        except:
            return None

    def decode_morse(self, text: str) -> Optional[str]:
        morse_code_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9'
        }
        try:
            morse_words = text.split(' / ')
            decoded_words = []
            for word in morse_words:
                decoded_chars = [morse_code_dict[char] for char in word.split()]
                decoded_words.append(''.join(decoded_chars))
            return ' '.join(decoded_words)
        except:
            return None

    def decode_unicode_escape(self, text: str) -> Optional[str]:
        try:
            return text.encode().decode('unicode-escape')
        except:
            return None

    def decode_reverse(self, text: str) -> str:
        return text[::-1]

    def decode_caesar(self, text: str) -> Optional[str]:
        try:
            # Return only shift 13 as an example
            shifted = ''.join(
                chr((ord(char) - ord('A' if char.isupper() else 'a') + 13) % 26
                    + ord('A' if char.isupper() else 'a')) if char.isalpha() else char
                for char in text)
            return f"Shift 13: {shifted}"
        except:
            return None

    def decode_atbash(self, text: str) -> Optional[str]:
        try:
            atbash = lambda c: chr(ord('Z') - (ord(c.upper()) - ord('A'))) if c.isalpha() else c
            return ''.join(atbash(c) for c in text)
        except:
            return None

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = DecoderGUI()
    app.run()
