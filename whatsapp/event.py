from .webdriver.validator_html.html_session import *
from .webdriver.validator_html.html_chat import *
from .core.message import *

class _EventCore:
    __events__ = [
        "loading", "pair_code", "pair_qrcode",
        "message", "catch",
    ]
    def __init__(self, driver, options):
        self._driver = driver
        self._options = options
        self._listener = {}
    
    def _session_login(self, _listener: dict[str, callable]):
        while True:
            loading_progress = check_loading_progress(self._driver)
            if loading_progress[0]:
                _listener['loading'](loading_progress[1])
                continue
            
            is_login = is_logged_in(self._driver)
            while not is_logged_in(self._driver):
                if self._options["type"] == "code":
                    phone_number = self._options["phone_number"]
                    click_login_with_phone_button(self._driver)
                    input_phone_number(self._driver, phone_number)
                    click_next_button(self._driver)
                    code = pairing_code(self._driver)
                    _listener['pair_code'](code)
                elif self._options["type"] == "qr":
                    code = pairing_qrcode(
                        self._driver,
                        self._options.get(
                        'qrcode_terminal', False)
                    )
                    _listener['pair_qrcode'](code)
            self._session_chat(_listener)
        
        def _session_chat(self, _listener: dict[str, callable]):
            cache = None
            while True:
                info = get_message(self._driver)
                if info:
                    if cache and cache == info:
                        continue
                    
                    for c in cache:
                        if c in info:
                            info.remove(c)
                    cache.append(info)
                    
                    msg = Message(
                        body=info['message'],
                        type='text'
                    )
                    
                    source = SourceMessage(
                        sender=info[0]['name'],
                        chat=info[0]['name'],
                        id=id(hex(info[0]['timestamp']))
                    )
                    
                    info = InfoMessage(
                        source=source,
                        name=info[0]['name'],
                        is_from_me=None,
                        timestamp=info[0]['timestamp']
                    )
                    _listener['message'](msg, info)
                    

class Event(_EventCore)
    def on(self, listen: str, callback: callable):
        self._listener[listen] = callback
    
    def run(self):
        try:
            self._session_login(self._listener)
        except (EOFError, KeyboardInterrupt) as e:
            if catch_callback := self._listener.get('catch'):
                catch_callback(EOFError, 'User forced to stop the program')
            else:
                raise EOFError('User forced to stop the program')
    
    def __repr__(self):
        return f"Event(driver={self._driver})"