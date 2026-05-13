#!/data/data/com.termux/files/usr/bin/python3.13
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os, subprocess as sp
import re
import json
import random
from datetime import datetime

# Konfigurasi path profil Firefox untuk menyimpan session
PATH_SAVING_SESSION = "~/.cache/mozilla/firefox/WI3YEIhY.Profile 1"
FIREFOX_PROFILE_DIR = os.path.expanduser(PATH_SAVING_SESSION)

# Konfigurasi waktu
WAIT_SCREENSHOT = 3
WAIT_INITIAL = 15
WAIT_TRANSITION = 5
SCREENSHOT_INTERVAL_LOADING = 5

# Konfigurasi screenshot
SCREENSHOT_DIR = "./screenshot-session"
START_TIME = datetime.now()
TIMESTAMP = START_TIME.strftime("%Y%m%d_%H%M%S")
ITERATION_COUNTER = 0
LOADING_SCREENSHOT_COUNTER = 0

# Konfigurasi file
CONFIG_FILE = "bot_config.json"

def load_phone_number():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("phone_number")
    except Exception as e:
        print(f"⚠️ Gagal load config: {e}")
    return None

def save_phone_number(phone):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"phone_number": phone}, f, indent=2)
        print(f"✅ Nomor tersimpan di {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️ Gagal simpan nomor: {e}")

def debug_html(html, path):
    path = f"./html-session/{path}"
    if not path.endswith(".html"):
        path += ".html"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 HTML debug saved: {path}")
    except Exception as e:
        print(f"❌ Gagal menyimpan HTML debug: {e}")

def setup_screenshot_dir():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        print(f"📁 Folder screenshot dibuat: {SCREENSHOT_DIR}")
        return
    
    if lst := os.listdir(SCREENSHOT_DIR):
        print(f"📁 Membersihkan folder screenshot: {SCREENSHOT_DIR}")
        for l in lst:
            if l.endswith(".png"):
                try:
                    os.remove(os.path.join(SCREENSHOT_DIR, l))
                except:
                    pass

def take_screenshot(driver, prefix=""):
    global ITERATION_COUNTER
    ITERATION_COUNTER += 1
    filename = f"{TIMESTAMP}-{ITERATION_COUNTER}{prefix}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    
    try:
        driver.save_screenshot(filepath)
        print(f"📸 Screenshot: {filename}")
        return True
    except Exception as e:
        print(f"❌ Gagal screenshot: {e}")
        return False

def initial_sleep(driver):
    print(f"\n⏳ Jeda awal {WAIT_INITIAL} detik...")
    for i in range(0, WAIT_INITIAL, WAIT_SCREENSHOT):
        print(f"   Detik ke-{i+1} dari {WAIT_INITIAL}")
        take_screenshot(driver, "_initial")
        if i + WAIT_SCREENSHOT < WAIT_INITIAL:
            time.sleep(WAIT_SCREENSHOT)
        else:
            remaining = WAIT_INITIAL - i
            if remaining > 0:
                time.sleep(remaining)

def transition_sleep(driver, reason=""):
    print(f"⏳ Jeda {WAIT_TRANSITION} detik ({reason})...")
    for i in range(0, WAIT_TRANSITION, WAIT_SCREENSHOT):
        take_screenshot(driver, f"_transition_{reason.replace(' ', '_')[:20]}")
        if i + WAIT_SCREENSHOT < WAIT_TRANSITION:
            time.sleep(WAIT_SCREENSHOT)
        else:
            remaining = WAIT_TRANSITION - i
            if remaining > 0:
                time.sleep(remaining)

def setup_firefox_profile():
    if not os.path.exists(FIREFOX_PROFILE_DIR):
        os.makedirs(FIREFOX_PROFILE_DIR, exist_ok=True)
        print(f"📁 Membuat profil Firefox baru di: {FIREFOX_PROFILE_DIR}")
        
        profile_ini = os.path.join(FIREFOX_PROFILE_DIR, "user.js")
        with open(profile_ini, "w") as f:
            f.write('''user_pref("dom.webdriver.enabled", false);
user_pref("useAutomationExtension", false);
user_pref("dom.push.enabled", true);
user_pref("dom.serviceWorkers.enabled", true);
''')
        print("✅ Profil Firefox baru berhasil dibuat")
    else:
        print(f"📁 Menggunakan profil Firefox yang sudah ada: {FIREFOX_PROFILE_DIR}")
    
    return FIREFOX_PROFILE_DIR

def save_debug_info(driver, filename_prefix="debug"):
    try:
        driver.save_screenshot(f"{filename_prefix}_screenshot.png")
        with open(f"{filename_prefix}_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        with open(f"{filename_prefix}_cookies.json", "w") as f:
            json.dump(driver.get_cookies(), f, indent=2)
        print(f"📁 Debug info saved: {filename_prefix}_*")
    except Exception as e:
        print(f"❌ Gagal menyimpan debug info: {e}")

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

def extract_chats_from_driver(driver):
    """Ekstrak daftar chat dari driver Selenium yang sedang berjalan"""
    print("\n📋 Mengekstrak daftar chat...")
    
    # Screenshot sebelum ekstraksi
    take_screenshot(driver, "_before_extract_chats")
    
    chats = []
    
    try:
        # Cari semua chat item
        chat_items = driver.find_elements(By.CSS_SELECTOR, "[data-testid='cell-frame-container']")
        print(f"✅ Ditemukan {len(chat_items)} chat items")
        import pprint
        
        for idx, item in enumerate(chat_items[:30]):  # Batasi 30 chat
            try:
                # Coba ekstrak nama/title
                title_elem = item.find_element(By.CSS_SELECTOR, "[title]")
                name = title_elem.get_attribute("title")
                
                # Coba ekstrak waktu
                time_elem = item.find_elements(By.CSS_SELECTOR, "[data-testid='cell-frame-primary-detail'] span")
                timestamp = time_elem[0].text if time_elem else "..."
                time_elem_dict = dir(time_elem[0])
                
                # Coba ekstrak pesan terakhir
                msg_elem = item.find_elements(By.CSS_SELECTOR, "[data-testid='last-msg-status'] span")
                last_msg = msg_elem[0].text if msg_elem else "(kosong)"
                msg_elem_dict = dir(msg_elem[0])
                
                # Coba ekstrak unread count
                unread_elem = item.find_elements(By.CSS_SELECTOR, "[data-testid='icon-unread-count'] span")
                unread = unread_elem[0].text if unread_elem else "0"
                unread_elem_dict = dir(unread_elem[0])
                print("="*60)
                print("(debugging)")
                print("="*60)
                print(f"timestamp: {time_elem_dict}")
                print(f"msg_elem: {msg_elem_dict}")
                print(f"unread_elem: {unread_elem_dict}")
                print("="*60)
                
                chats.append({
                    'name': name,
                    'timestamp': timestamp,
                    'last_message': last_msg,
                    'unread_count': unread
                })
                
            except Exception as e:
                continue
        
        take_screenshot(driver, "_after_extract_chats")
        
    except Exception as e:
        print(f"❌ Gagal ekstrak chat: {e}")
    
    return chats

def click_chat_by_name(driver, chat_name):
    """Klik chat berdasarkan nama kontak/grup"""
    print(f"\n🔍 Mencari chat: {chat_name}")
    take_screenshot(driver, "_searching_chat")
    
    try:
        # Cari elemen chat dengan title
        chat_elem = driver.find_element(By.XPATH, f"//div[@title='{chat_name}']")
        chat_elem.click()
        print(f"✅ Chat '{chat_name}' diklik")
        transition_sleep(driver, "after_click_chat")
        return True
    except:
        # Coba dengan partial match
        try:
            chat_elem = driver.find_element(By.XPATH, f"//div[contains(@title, '{chat_name}')]")
            chat_elem.click()
            print(f"✅ Chat (partial) '{chat_name}' diklik")
            transition_sleep(driver, "after_click_chat_partial")
            return True
        except Exception as e:
            print(f"❌ Gagal menemukan chat '{chat_name}': {e}")
            return False

def send_message_to_chat(driver, phone_number, message):
    """
    Kirim pesan ke nomor telepon
    
    Args:
        driver: WebDriver instance
        phone_number: Nomor telepon tujuan (format: 628123456789)
        message: Pesan yang akan dikirim
    """
    print(f"\n💬 Mengirim pesan ke: {phone_number}")
    print(f"📝 Pesan: {message}")
    
    take_screenshot(driver, "_before_send_message")
    
    try:
        # Cari input box pesan
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@contenteditable='true' and @data-testid='conversation-compose-box-input']"
            ))
        )
        
        message_box.click()
        transition_sleep(driver, "before_type_message")
        
        # Ketik pesan
        message_box.clear()
        time.sleep(0.5)
        message_box.send_keys(message)
        take_screenshot(driver, "_after_type_message")
        
        # Kirim dengan Enter
        message_box.send_keys(Keys.ENTER)
        print("✅ Pesan berhasil dikirim!")
        
        transition_sleep(driver, "after_send_message")
        take_screenshot(driver, "_message_sent")
        
        return True
        
    except Exception as e:
        print(f"❌ Gagal mengirim pesan: {e}")
        take_screenshot(driver, "_send_message_error")
        return False

def send_message_by_number(driver, target_number, message):
    """
    Kirim pesan ke nomor telepon dengan membuka chat baru
    
    Args:
        driver: WebDriver instance
        target_number: Nomor telepon tujuan (format: 628123456789)
        message: Pesan yang akan dikirim
    """
    print(f"\n📱 Mencari/membuka chat dengan nomor: {target_number}")
    take_screenshot(driver, "_before_new_chat")
    
    try:
        # Cari tombol New Chat
        new_chat_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='new-chat-outline']")
        new_chat_btn.click()
        print("✅ Tombol New Chat diklik")
        transition_sleep(driver, "after_new_chat_click")
        
        # Cari input pencarian
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//input[(@role='textbox' and @dir='ltr') or contains(@class, 'html-input')]"
            ))
        )
        search_box.click()
        search_box.send_keys(target_number)
        print(f"✅ Nomor {target_number} dimasukkan")
        transition_sleep(driver, "after_type_number")
        
        # Cari hasil pencarian dan klik
        try:
            contact = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    f"//div[contains(@title, '{target_number}') or contains(@title, '{target_number[-8:]}')]"
                ))
            )
            contact.click()
            print("✅ Kontak ditemukan dan diklik")
            transition_sleep(driver, "after_click_contact")
        except:
            # Jika tidak ditemukan, coba tekan Enter
            search_box.send_keys(Keys.ENTER)
            transition_sleep(driver, "after_enter_number")
        
        # Kirim pesan
        return send_message_to_chat(driver, target_number, message)
        
    except Exception as e:
        print(f"❌ Gagal membuka chat baru: {e}")
        take_screenshot(driver, "_new_chat_error")
        return False

def click_login_with_phone_button(driver):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[@data-testid='link-device-qrcode-alt-linking-hint']"
            ))
        )
        element.click()
        print("✅ Tombol 'Log in with phone number' diklik")
        return True
    except:
        pass
    print("❌ Tombol 'Log in with phone number' tidak ditemukan")
    return False

def input_phone_number(driver):
    print("\n📱 Mencari form input nomor telepon...")
    
    phone_input = None
    
    try:
        phone_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//input[@data-testid='phone-number-input' and @dir='ltr']"
            ))
        )
        print(f"✅ Input phone ditemukan")
    except:
        pass
    
    if not phone_input:
        print("❌ Input nomor telepon tidak ditemukan")
        return False
    
    phone_number = load_phone_number()
    
    if not phone_number:
        phone_number = input("📱 Masukkan nomor WhatsApp (contoh: 8123456789): ").strip()
        phone_number = re.sub(r'[^0-9]', '', phone_number)
        if phone_number.startswith("0"):
            phone_number = "62" + phone_number[1:]
        elif not phone_number.startswith("62"):
            phone_number = "62" + phone_number
        save_phone_number(phone_number)
    else:
        print(f"📱 Menggunakan nomor tersimpan: {phone_number}")
    
    phone_input.clear()
    time.sleep(1)
    phone_input.send_keys(phone_number)
    print(f"✅ Nomor {phone_number} berhasil dimasukkan")
    time.sleep(2)
    
    return True

def click_next_button(driver):
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
            print("✅ Tombol Next diklik")
            return True
        except:
            continue
    
    print("❌ Tombol Next tidak ditemukan")
    return False

def wait_for_pairing_code(driver, timeout=60):
    print("\n🔍 Menunggu Pairing Code dari WhatsApp...")
    
    start_time = time.time()
    code_cells_selector = (By.CSS_SELECTOR, "div[data-link-code]")
    
    while time.time() - start_time < timeout:
        time.sleep(1)
        
        if int(time.time() - start_time) % 5 == 0:
            take_screenshot(driver, "_waiting_code")
        
        try:
            cells = driver.find_elements(*code_cells_selector)
            raw_code = cells.get_attribute("data-link-code")
            
            pairing_code = raw_code.replace(",", "")
            
            print("\n" + "="*60)
            print("🎉 PAIRING CODE DITEMUKAN!")
            print("="*60)
            print(f"📱 KODE: {pairing_code}")
            print("="*60)
            print("\n📌 LANGKAH SELANJUTNYA:")
            print("1. Buka WhatsApp di HP")
            print("2. Pengaturan > Perangkat Tertaut")
            print("3. Pilih 'Tautkan dengan nomor telepon'")
            print(f"4. Masukkan kode: {pairing_code}")
            print("="*60 + "\n")
            
            with open("pairing_code.txt", "w") as f:
                f.write(pairing_code)
            return True
                        
        except Exception as e:
            pass
        
        if int(time.time() - start_time) % 10 == 0 and int(time.time() - start_time) > 0:
            debug_html(driver.page_source, "./pairingCode_debug.html")
    
    print("❌ Pairing Code tidak ditemukan dalam timeout")
    return False

def handle_pairing_code_login(driver):
    print("\n" + "="*60)
    print("🔐 MEMULAI PROSES PAIRING CODE")
    print("="*60)
    
    debug_html(driver.page_source, "./login.html")
    
    if not click_login_with_phone_button(driver):
        print("❌ Gagal menemukan tombol login")
        return False
    
    transition_sleep(driver, "after_click_phone_login")
    
    debug_html(driver.page_source, "./input.html")
    if not input_phone_number(driver):
        print("❌ Gagal input nomor telepon")
        return False
    
    if not click_next_button(driver):
        print("❌ Gagal klik tombol Next")
        return False
    
    if wait_for_pairing_code(driver):
        print("✅ Pairing Code berhasil didapatkan!")
        return True
    else:
        print("❌ Gagal mendapatkan Pairing Code")
        return False

def show_command():
    print("\n" + "="*60)
    print("🤖 MODE INTERAKTIF BOT WHATSAPP")
    print("="*60)
    print("Perintah yang tersedia:")
    print("  1. list         - Tampilkan daftar chat")
    print("  2. send         - Kirim pesan ke nomor")
    print("  3. extract      - Ekstrak semua chat ke file")
    print("  4. screenshot   - Ambil screenshot manual")
    print("  5. refresh      - Refresh daftar chat")
    print("  6. html         - Mengekstrak Page saat ini menjadi file html")
    print("  7. help         - Menampilkan Daftar perintah")
    print("  8. clear        - Membersihkan terminal")
    print("  9. exit         - Keluar dari bot")
    print("="*60)


def interactive_mode(driver):
    """Mode interaktif untuk mengirim pesan"""
    
    show_command()
    
    while True:
        try:
            cmd = input("\n💡 Masukkan perintah: ").strip().lower()
            
            if cmd == "list":
                chats = extract_chats_from_driver(driver)
                print("\n📋 DAFTAR CHAT:")
                print("-" * 60)
                for i, chat in enumerate(chats[:20]):
                    print("="*60)
                    print(f"{i+1}. {chat['name']}")
                    print("="*60)
                    print(f"waktu terakhir: {chat['timestamp']}")
                    print(f"total chat belum terbaca: {chat['unread_count']}")
                    print("="*60)
                    print(chat['last_message'])
                    print("="*60)
                    print()
                    time.sleep(0.75)
                    
            elif cmd == "send":
                target = input("📱 Masukkan nomor telepon tujuan (contoh: 628123456789): ").strip()
                target = re.sub(r'[^0-9]', '', target)
                if not target.startswith("62"):
                    if target.startswith("0"):
                        target = "62" + target[1:]
                    else:
                        target = "62" + target
                
                message = input("💬 Masukkan pesan: ").strip()
                
                if message:
                    confirm = input(f"\n✅ Kirim '{message}' ke {target}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        print("\n📤 Mengirim pesan...")
                        if send_message_by_number(driver, target, message):
                            print("✅ Pesan berhasil dikirim!")
                            take_screenshot(driver, "_message_sent_success")
                        else:
                            print("❌ Gagal mengirim pesan")
                else:
                    print("❌ Pesan tidak boleh kosong!")
                    
            elif cmd == "extract":
                print("\n📥 Mengekstrak semua chat...")
                take_screenshot(driver, "_extract_all_chats")
                
                # Ekstrak dari page source
                chats = extract_chats_from_driver(driver)
                
                # Simpan ke file
                with open("extracted_chats.json", "w", encoding="utf-8") as f:
                    json.dump(chats, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {len(chats)} chat berhasil diekstrak ke extracted_chats.json")
                
                # Tampilkan ringkasan
                print("\n📋 RINGKASAN CHAT:")
                for i, chat in enumerate(chats[:10]):
                    print("="*60)
                    print(f"{i+1}. {chat['name']}:")
                    print("="*60)
                    print(f"{chat['last_message']}")
                    
            elif cmd == "screenshot":
                take_screenshot(driver, "_manual")
                print("✅ Screenshot diambil")
                
            elif cmd == "refresh":
                print("🔄 Merefresh halaman...")
                driver.refresh()
                transition_sleep(driver, "after_refresh")
                print("✅ Refresh selesai")
            
            elif cmd == "html":
                debug_html(driver.page_source, "./page_now.html")
            
            elif cmd == "help":
                show_command()
            
            elif cmd == "clear":
                sp.run(["clear"])
                show_command()
            
            elif cmd == "exit":
                print("👋 Keluar dari bot...")
                break
                
            else:
                print("❌ Perintah tidak dikenal. Gunakan: list, send, extract, screenshot, refresh, exit")
                
        except KeyboardInterrupt:
            print("\n👋 Keluar...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            take_screenshot(driver, "_error")

def main():
    global driver_global
    
    setup_screenshot_dir()
    profile_path = setup_firefox_profile()
    
    gecko_path = os.popen("which geckodriver").read().strip()
    if not gecko_path:
        print("❌ Geckodriver tidak ditemukan. Install: pkg install geckodriver")
        return
    
    options = Options()
    options.add_argument(f"-profile")
    options.add_argument(profile_path)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--headless")
    
    service = Service(executable_path=gecko_path)
    
    print("🚀 Membuka WhatsApp Web...")
    driver_global = webdriver.Firefox(service=service, options=options)
    driver_global.get("https://web.whatsapp.com/")
    
    initial_sleep(driver_global)

    if wait_for_loading_complete(driver_global, timeout=120) or is_logged_in(driver_global):
        debug_html(driver_global.page_source, "./page_now.html")
        print("✅ Session valid! Bot langsung aktif.")
    else:
        print("\n🔐 Session tidak ditemukan. Memerlukan login via Pairing Code.")
        
        success = handle_pairing_code_login(driver_global)
        
        if not success:
            print("\n❌ Gagal login. Silakan coba lagi.")
            driver_global.quit()
            return
        
        debug_html(driver_global.page_source, "./page_now.html")
        loading_success = wait_for_loading_complete(driver_global, timeout=60)
        
        if not loading_success:
            print("⚠️ Loading belum selesai, tetapi melanjutkan...")
        
        if is_logged_in(driver_global):
            print("\n💾 Menyimpan session ke profil Firefox...")
            save_debug_info(driver_global, "session_saved")
            print("✅ Session berhasil disimpan!")
    
    
    # Bot loop fallback
    try:
        # Jalankan mode interaktif
        print("\n🤖 Bot siap digunakan!")
        interactive_mode(driver_global)
        print("📸 Screenshot disimpan di folder './screenshot-session'")
        print("💡 Ketik 'exit' untuk berhenti, atau gunakan perintah di atas\n")
        
        while True:
            time.sleep(5)
            if "WhatsApp" in driver_global.title:
                pass
                
    except KeyboardInterrupt:
        print("\n⏹️ Bot dihentikan")
    finally:
        try:
            save_debug_info(driver_global, "final_state")
            print(f"📁 Total screenshot: {ITERATION_COUNTER}")
            exit(0)
        except:
            exit(1)
        finally:
            driver_global.quit()
            

driver_global = None

def wait_for_loading_complete(driver, timeout=120):
    global LOADING_SCREENSHOT_COUNTER
    
    print("\n⏳ Menunggu loading WhatsApp Web selesai...")
    start_time = time.time()
    last_screenshot_time = start_time
    
    while time.time() - start_time < timeout:
        current_time = time.time()
        if current_time - last_screenshot_time >= SCREENSHOT_INTERVAL_LOADING:
            take_screenshot(driver, f"_loading_{LOADING_SCREENSHOT_COUNTER}")
            LOADING_SCREENSHOT_COUNTER += 1
            last_screenshot_time = current_time
            debug_html(driver_global.page_source,
            f"./login_partOf{LOADING_SCREENSHOT_COUNTER}.html")
        
        if is_logged_in(driver):
            print("✅ Loading selesai! WhatsApp siap digunakan.")
            take_screenshot(driver, "_loading_complete")
            return True
        
        # Cek elemen loading
        try:
            loading_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'loading') or contains(@class, 'progress')]")
            if loading_elements:
                print("⏳ Masih loading...")
        except:
            pass
        
        time.sleep(2)
    
    print("⚠️ Timeout menunggu loading selesai")
    return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Bot dihentikan")
        exit(0)
