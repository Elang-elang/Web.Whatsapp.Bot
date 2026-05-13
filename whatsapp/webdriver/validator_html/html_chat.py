from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re
import time

REGEX_TIMESTAMP = {
    "HOUR": r"(\d{2}).(\d{2})",
    "YESTERDAY": r"Kemaren",
    "YEARS": r"(\d{2})//(\d{2})//(\d{2})",
}

def _core_send_message(driver, message):
    try:
        # Cari input box pesan
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@contenteditable='true' and @data-testid='conversation-compose-box-input']"
            ))
        )
        
        message_box.click()
        time.sleep(0.5)

        # Ketik pesan
        message_box.clear()
        time.sleep(0.5)
        for msg in message:
            message_box.send_keys(msg)

        # Kirim dengan Enter
        message_box.send_keys(Keys.ENTER)

        return True
        
    except Exception as e:
        return False

def send_message(driver, target: str, message: str):
    try:
        # Cari tombol New Chat
        new_chat_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='new-chat-outline']")
        new_chat_btn.click()
        
        time.sleep(0.5)
        # Cari input pencarian
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//input[(@role='textbox' and @dir='ltr') or contains(@class, 'html-input')]"
            ))
        )
        search_box.click()
        for char in target:
            search_box.send_keys(char)
        
        time.sleep(0.5)
        # Cari hasil pencarian dan klik
        try:
            contact = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"//div[contains(@title, '{target}')]"
                ))
            )
            contact.click()
        except:
            # Jika tidak ditemukan, coba tekan Enter
            search_box.send_keys(Keys.ENTER)
        # Kirim pesan
        return _core_send_message(driver, message)
        
    except Exception as e:
        return False

def get_message(driver):
    chats = []
    try:
        chat_items = driver.find_elements(By.CSS_SELECTOR, "[data-testid='cell-frame-container']")
        for idx, item in chat_items:
            try:
                # Coba ekstrak unread count
                unread_elem = item.find_elements(By.CSS_SELECTOR, "[data-testid='icon-unread-count'] span")
                unread = int(unread_elem[0].text if unread_elem else "0")
                if not unread:
                    continue
                
                title_elem = item.find_element(By.CSS_SELECTOR, "[title]")
                name = title_elem.get_attribute("title")
                # Coba ekstrak waktu
                timestamp = None
                time_elem = item.find_elements(By.CSS_SELECTOR, "[data-testid='cell-frame-primary-detail'] span")
                raw_time = time_elem[0].text if time_elem else None
                try:
                    if re.match(REGEX_TIMESTAMP["HOUR"], raw_time):
                        timestamp = datetime.strptime(raw_time, "%H.%M")
                    elif re.match(REGEX_TIMESTAMP["YESTERDAY"], raw_time):
                        timestamp = datetime.now() - timedelta(days=1)
                    elif re.match(REGEX_TIMESTAMP["YEARS"], raw_time):
                        timestamp = datetime.strptime(raw_time, "%d/%m/%y")
                    else:
                        timestamp = None
                except:
                    timestamp = None
                # Coba ekstrak pesan terakhir
                msg_elem = item.find_elements(By.CSS_SELECTOR, "[data-testid='last-msg-status'] span")
                last_msg = msg_elem[0].text if msg_elem else None
                
                chats.append({
                    'name': name,
                    'timestamp': timestamp,
                    'message': last_msg,
                })
                
            except Exception as e:
                continue
        
    except Exception as e:
        pass
    
    return chats