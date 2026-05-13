from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .webdriver.socket import Socket
from .event import Event

import pathlib as P
import typing as T
import time

class Bot:
    def __init__(
        self,
        *,
        session_path:       T.Option[str | P.PosixPath] = None,
        pair_options:       T.Dict[str, T.Any]          = {},
        options:            T.Dict[str, T.Any]          = {},
    ) -> T.Self:
        """
        Bot untuk membangun bot whatsapp
        
        Args:
            session_path:       Tempat penyimpanan Sesi web
            pair_options:       Opsi untuk pair (penghubungan) bot wa dengan whatsapp web dengan
                                berbagai opsi sebagai berikut:
                                - type:             untuk menyatakan apakah mau kode atau qr (val: "code", "qr")
                                - phone_number:     untuk nomer telepon nya (kalau "type": "code")
                                - qrcode_terminal:  untuk mengkonsol qrcode pada terminal tanpa ribet
                                                    (kalau: "type": "qr")
                                
            options:            Untuk menyatakan apa saja yang ingin disertakan saat menjalankan bot
                                wa ini. Isi kurang lebih dari options ini:
                                {
                                    "browser": "chrome",
                                    "headless": True,
                                    "arguments": ["--no-sandbox"],
                                    "service": {
                                        "executable_path": None,
                                    }
                                }
                                - browser:                  (opsional)      browsernya, bawaan: firefox
                                - headless:                 (opsional)      alias dari {"arguments": ["--headless"]} , bawaan tidak (false) # terpisah
                                - arguments:                (opsional)      untuk argument-argument lainnya
                                - service:                  (optional)      untuk service dan ini isi service:
                                    - executable_path:      (optional)      untuk mengeksekusi dari path, seperti
                                                                            geckodriver
                                                                            
                                    - port:                 (optional)      port untuk menjalankan executable_path
                                    - service_args:         (optional)      argument-argument untuk menjalankan
                                                                            executable_path
                                                                            
                                    - env:                  (optional)      mapping variabel environment
                                    - driver_path_env_key:  (optional)      variabel environment yang dibutuhkan
                                                                            executable_path
        """
        self.session_path       = str(session_path)
        self.options            = options
        
        self.DriverSocket = Socket(session_path, options)
        self.Event = Event(self.DriverSocket, pair_options)
        self.is_running = False
        
    def on(self, listen: str, callback: callabe):
        self.Event.on(listen, callback)
    
    def start(self):
        self.is_running = True
        try:
            print("[std:console] bot is running")
            self.DriverSocket.run()
            self.Event.run()
        except EOFError as e:
            print("[std:err-io]  error because 'EOFError'")
            print("[std:console] bot is finish")
            exit(0)
        except KeyboardInterrupt as e:
            print("[std:err-io]  error because 'KeyboardInterrupt'")
            print("[std:console] bot is finish")
            exit(0)
    
    def __repr__(self):
        return f"Bot(is_running={is_running})"