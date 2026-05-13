from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def check_loading_progress(driver):
    """
    Cek progress loading WhatsApp Web
    Returns: (is_loading, progress_percentage)
    """
    try:
        # Cari elemen progress bar
        progress_selectors = [
            (By.TAG_NAME, "progress"),
            (By.XPATH, "//progress"),
            (By.XPATH, "//div[@role='progressbar']"),
        ]
        
        for by, selector in progress_selectors:
            try:
                elements = driver.find_elements(by, selector)
                for elem in elements:
                    if elem.is_displayed():
                        progress_value = None
                        max_value = None
                        
                        # Cek attribute value
                        value = elem.get_attribute("value")
                        if value and value.isdigit():
                            progress_value = float(value)
                        
                        # Cek attribute max
                        max_attr = elem.get_attribute("max")
                        if max_attr and max_attr.isdigit():
                            max_value = float(max_attr)
                        
                        if progress_value is not None and max_value is not None and max_value > 0:
                            percentage = (progress_value / max_value) * 100
                            # Masih loading jika progress < max
                            if progress_value < max_value:
                                return True, percentage
                            else:
                                return False, 100
                        else:
                            # Progress bar tanpa value, anggap masih loading
                            return True, None
            except:
                continue
        
        # Cek apakah ada elemen loading lain
        loading_texts = [
            "loading", "connecting", "connecting to chat",
            "initializing", "starting up"
        ]
        
        page_source = driver.page_source.lower()
        for text in loading_texts:
            if text in page_source:
                return True, None
        
        return False, None
        
    except Exception as e:
        return False, None

def click_login_with_phone_button(driver):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[@data-testid='link-device-qrcode-alt-linking-hint']"
            ))
        )
        element.click()
        return True
    except Exception as e:
        pass
    return False

def input_phone_number(driver, phone_number):
    phone_input = None
    
    try:
        phone_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//input[@data-testid='phone-number-input' and @dir='ltr']"
            ))
        )
    except:
        pass
    
    if not phone_input:
        return False
    
    # Input nomor
    phone_input.clear()
    time.sleep(1)
    phone_input.send_keys(phone_number)
    time.sleep(2)
    
    return True

def click_next_button(driver):
    """Klik tombol Next setelah input nomor"""
    # Coba berbagai selector
    next_selectors = [
        (By.XPATH, "//button[@data-testid='start-phone-number-login-button']"),
        (By.XPATH, "//button[contains(@class, 'html-button') and (@type='button')]//span[text()='Next']/.."),
        (By.XPATH, "//button[.//span[text()='Next']]"),
        (By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'Lanjut')]"),
    ]
    
    for by, selector in next_selectors:
        try:
            next_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((by, selector))
            )
            next_btn.click()
            return True
        except:
            continue
    
    return False

def pairing_code(driver):
    code_cells_selector = (By.CSS_SELECTOR, "div[data-testid='link-with-phone-number-code-cells']")
    cell = driver.find_element(*code_cells_selector)
    raw_code = cells.get_attribute('data-link-code')
    code = raw_code.replace(",", "")
    return code

def pairing_qrcode(driver, is_print: bool = False):
    cell = driver.find_element(By.CSS_SELECTOR, "canvas[role='img']")
    qrcode_base64 = cell.screenshot_as_base64
    if is_print:
        import qrcode
        import base64
        import io
        from PIL import Image
        
        img = Image.open(io.BytesIO(base64.b64decode(qrcode_base64))).convert("1")
        qr = qrcode.QRCode(border=0)
        qr.modules = [[img.getpixel((x, y)) == 0 for x in range(img.width)] for y in range(img.height)]
        qr.modules_count = img.width
        qr.print_ascii(invert=False)
    return qrcode_base64

def is_logged_in(driver):
    try:
        if "chat.whatsapp.com" in driver.current_url:
            return True
        
        chat_list_selectors = [
            (By.XPATH, "//div[@data-testid='chat-list']"),
            (By.XPATH, "//div[@aria-label='Chat list']"),
            (By.CSS_SELECTOR, "[data-testid='chat-list']"),
        ]
        
        for by, selector in chat_list_selectors:
            try:
                driver.find_element(by, selector)
                return True
            except:
                continue
        return False
    except:
        return False