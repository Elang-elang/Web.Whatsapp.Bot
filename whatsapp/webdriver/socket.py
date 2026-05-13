from selenium import webdriver
import os

type MISSING_OPTION = None

class Options:
    __options__ = {
        'firefox': webdriver.FirefoxOptions,
        'chrome':  webdriver.ChromeOptions,
        'edge':    webdriver.EdgeOptions,
        'safari':  webdriver.SafariOptions,
    }
    def __new__(cls, socket):
        res = cls.__options__.get(socket, MISSING_OPTION)
        if res is MISSING_OPTION:
            raise Exceptions('Cannot get options')
        return res

class Service:
    __options__ = {
        'firefox': webdriver.FirefoxService,
        'chrome':  webdriver.ChromeService,
        'edge':    webdriver.EdgeService,
        'safari':  webdriver.SafariService,
    }
    def __new__(cls, socket):
        res = cls.__options__.get(socket, MISSING_OPTION)
        if res is MISSING_OPTION:
            raise Exceptions('Cannot get service')
        return res

class Socket:
    __options__ = {
        'firefox': webdriver.Firefox,
        'chrome':  webdriver.Chrome,
        'edge':    webdriver.Edge,
        'safari':  webdriver.Safari,
    }
    def __init__(
        self,
        profile_path,
        options = {}
    ):
        self.socket = self.__options__.get(options.get("browser", "firefox"), MISSING_OPTION)
        if self.socket is MISSING_OPTION:
            raise Exceptions('Cannot get socket')
        
        self._options = Options(socket)()
        self._service = Service(socket)
        
        self.add_argument("--profile")
        self.add_argument(profile_path)
        
        options.pop("browser") if options.get("browser", None) else None
        self._parse_options(options)
    
    def _parse_options(self, options):
        for name, value in options.items():
            if name == "add_argument":
                for val in value:
                    self._options.add_argument(val)
            if name == "headless" and value:
                self._options.add_argument("--headless")
            if name == "service":
                if isinstance(value, dict):
                    self._service = self._service(**value)
                elif isinstance(value, (list, set, tuple)):
                    self._service = self._service(*value)
    
    def __repr__(self):
        socket  = repr(self.socket)
        options = repr(self._options)
        service = repr(self._service)
        return f"socket(socket={socket}, options={options}, service={service})"
    
    def run(self):
        driver = self.socket(service=self.service, options=self.options)
        driver.get("https://web.whatsapp.com/")
        return driver
