#!/data/data/com.termux/files/usr/bin/python3.13
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re
import json
import random
from datetime import datetime

# Konfigurasi path profil Firefox untuk menyimpan session
PATH_SAVING_SESSION = "~/.cache/mozilla/firefox/uvisv5e1.whatsapp-bot/"
FIREFOX_PROFILE_DIR = os.path.expanduser(PATH_SAVING_SESSION)

# Konfigurasi waktu
WAIT_SCREENSHOT = 3
WAIT_INITIAL = 15  # Jeda awal FIX 15 detik
WAIT_TRANSITION = 5  # Jeda transisi FIX 5 detik
SCREENSHOT_INTERVAL_LOADING = 5  # Screenshot setiap 5 detik saat loading

# Konfigurasi screenshot
SCREENSHOT_DIR = "./screenshot-session"
START_TIME = datetime.now()
TIMESTAMP = START_TIME.strftime("%Y%m%d_%H%M%S")
ITERATION_COUNTER = 0
LOADING_SCREENSHOT_COUNTER = 0

# Konfigurasi file
CONFIG_FILE = "bot_config.json"

def load_phone_number():
    """Load nomor telepon dari file config"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("phone_number")
    except Exception as e:
        print(f"⚠️ Gagal load config: {e}")
    return None

def save_phone_number(phone):
    """Simpan nomor telepon ke file config"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"phone_number": phone}, f, indent=2)
        print(f"✅ Nomor tersimpan di {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️ Gagal simpan nomor: {e}")

def debug_html(html, path):
    """Simpan HTML untuk debugging"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 HTML debug saved: {path}")
    except Exception as e:
        print(f"❌ Gagal menyimpan HTML debug: {e}")

def setup_screenshot_dir():
    """Buat folder screenshot"""
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
    """Ambil screenshot dengan format waktu dan iterasi"""
    global ITERATION_COUNTER
    ITERATION_COUNTER += 1
    filename = f"{TIMESTAMP}-{ITERATION_COUNTER}{prefix}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    
    try:
        driver.save_screenshot(filepath)
        return True
    except Exception as e:
        print(f"❌ Gagal screenshot: {e}")
        return False

def initial_sleep(driver):
    """Jeda awal FIX 15 detik dengan screenshot"""
    print(f"\n⏳ Jeda awal {WAIT_INITIAL} detik...")
    for i in range(0, WAIT_INITIAL, WAIT_SCREENSHOT):
        print(f"   Detik ke-{i+1} dari {WAIT_INITIAL}")
        take_screenshot(driver)
        if i + WAIT_SCREENSHOT < WAIT_INITIAL:
            time.sleep(WAIT_SCREENSHOT)
        else:
            # Sisa waktu
            remaining = WAIT_INITIAL - i
            if remaining > 0:
                time.sleep(remaining)

def transition_sleep(driver):
    """Jeda transisi FIX 5 detik dengan screenshot"""
    print(f"⏳ Jeda {WAIT_TRANSITION} detik...")
    for i in range(0, WAIT_TRANSITION, WAIT_SCREENSHOT):
        take_screenshot(driver)
        if i + WAIT_SCREENSHOT < WAIT_TRANSITION:
            time.sleep(WAIT_SCREENSHOT)
        else:
            remaining = WAIT_TRANSITION - i
            if remaining > 0:
                time.sleep(remaining)

def setup_firefox_profile():
    """Setup profil Firefox untuk session persistence"""
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
    """Simpan informasi debugging"""
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
    """Cek apakah sudah login ke WhatsApp"""
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
        print(f"⚠️ Error checking loading: {e}")
        return False, None

def wait_for_loading_complete(driver, timeout=120):
    """
    Tunggu hingga loading selesai
    Screenshot setiap SCREENSHOT_INTERVAL_LOADING detik
    """
    global LOADING_SCREENSHOT_COUNTER
    
    print("\n⏳ Menunggu loading WhatsApp Web selesai...")
    start_time = time.time()
    last_screenshot_time = start_time
    
    while time.time() - start_time < timeout:
        is_loading, progress = check_loading_progress(driver)
        
        # Screenshot setiap interval
        current_time = time.time()
        if current_time - last_screenshot_time >= SCREENSHOT_INTERVAL_LOADING:
            take_screenshot(driver, f"_loading_{LOADING_SCREENSHOT_COUNTER}")
            LOADING_SCREENSHOT_COUNTER += 1
            last_screenshot_time = current_time
        
        if not is_loading:
            # Cek apakah sudah login
            if is_logged_in(driver):
                print("✅ Loading selesai! WhatsApp siap digunakan.")
                take_screenshot(driver, "_loading_complete")
                return True
            else:
                time.sleep(2)
                continue
        
        if progress is not None:
            print(f"📊 Progress loading: {progress:.1f}%")
        else:
            print("⏳ Masih loading...")
        
        time.sleep(2)
    
    print("⚠️ Timeout menunggu loading selesai")
    return False

def click_login_with_phone_button(driver):
    """Klik tombol 'Log in with phone number'"""
    
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[@data-testid='link-device-qrcode-alt-linking-hint']"
            ))
        )
        print(f"✅ Tombol ditemukan: {element}")
        element.click()
        print("✅ Tombol 'Log in with phone number' diklik")
        return True
    except:
        pass
    
    print("❌ Tombol 'Log in with phone number' tidak ditemukan")
    return False

def input_phone_number(driver):
    """Input nomor telepon ke form Pairing Code"""
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
    
    # Coba load nomor dari config
    phone_number = load_phone_number()
    
    if not phone_number:
        # Minta user input nomor
        phone_number = input("📱 Masukkan nomor WhatsApp (contoh: 8123456789): ").strip()
        
        # Format nomor
        phone_number = re.sub(r'[^0-9]', '', phone_number)
        if phone_number.startswith("0"):
            phone_number = "62" + phone_number[1:]
        elif not phone_number.startswith("62"):
            phone_number = "62" + phone_number
        
        # Simpan untuk下次
        save_phone_number(phone_number)
    else:
        print(f"📱 Menggunakan nomor tersimpan: {phone_number}")
    
    # Input nomor
    phone_input.clear()
    time.sleep(1)
    phone_input.send_keys(phone_number)
    print(f"✅ Nomor {phone_number} berhasil dimasukkan")
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
            print(f"✅ Tombol Next ditemukan dengan selector: {selector}")
            next_btn.click()
            print("✅ Tombol Next diklik")
            return True
        except:
            continue
    
    print("❌ Tombol Next tidak ditemukan")
    return False

def wait_for_pairing_code(driver, timeout=60):
    """Tunggu dan ekstrak Pairing Code 8 digit"""
    print("\n🔍 Menunggu Pairing Code dari WhatsApp...")
    
    start_time = time.time()
    
    # Selector untuk code cells (perbaikan)
    code_cells_selector = (By.CSS_SELECTOR, "div[data-testid='link-with-phone-number-code-cells']")
    
    while time.time() - start_time < timeout:
        time.sleep(1)
        
        # Screenshot setiap 5 detik
        if int(time.time() - start_time) % 5 == 0:
            take_screenshot(driver, "_waiting_code")
        
        try:
            # Cari semua cell kode
            cells = driver.find_elements(*code_cells_selector)
            
            if cells and len(cells) >= 4:
                # Gabungkan teks dari 4 cell pertama
                code_parts = []
                for cell in cells[:4]:
                    text = cell.text.strip()
                    if text and text.isdigit():
                        code_parts.append(text)
                
                if len(code_parts) == 4:
                    pairing_code = ''.join(code_parts)
                    
                    if len(pairing_code) == 8 and pairing_code.isdigit():
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
            
            # Fallback: cek attribute data-link-code
            code_elements = driver.find_elements(By.CSS_SELECTOR, "[data-link-code]")
            for elem in code_elements:
                raw_code = elem.get_attribute("data-link-code")
                if raw_code:
                    pairing_code = raw_code.replace(",", "").strip()
                    if len(pairing_code) == 8 and pairing_code.isdigit():
                        print("\n" + "="*60)
                        print("🎉 PAIRING CODE DITEMUKAN!")
                        print("="*60)
                        print(f"📱 KODE: {pairing_code}")
                        print("="*60 + "\n")
                        
                        with open("pairing_code.txt", "w") as f:
                            f.write(pairing_code)
                        return True
                        
        except Exception as e:
            # Silent fail, continue loop
            pass
        
        # Debug HTML setiap 10 detik
        if int(time.time() - start_time) % 10 == 0 and int(time.time() - start_time) > 0:
            debug_html(driver.page_source, "./pairingCode_debug.html")
    
    print("❌ Pairing Code tidak ditemukan dalam timeout")
    return False

def handle_pairing_code_login(driver):
    """Flow lengkap Pairing Code login"""
    print("\n" + "="*60)
    print("🔐 MEMULAI PROSES PAIRING CODE")
    print("="*60)
    
    debug_html(driver.page_source, "./login.html")
    
    if not click_login_with_phone_button(driver):
        print("❌ Gagal menemukan tombol login")
        return False
    
    transition_sleep(driver)
    
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
    
    # Jeda awal FIX 15 detik
    initial_sleep(driver_global)

    # Cek apakah sudah login
    if wait_for_loading_complete(driver_global, timeout=60) or is_logged_in(driver_global):
        debug_html(driver_global.page_source, "./page_now.html")
        print("✅ Session valid! Bot langsung aktif.")
    else:
        print("\n🔐 Session tidak ditemukan. Memerlukan login via Pairing Code.")
        
        success = handle_pairing_code_login(driver_global)
        
        if not success:
            print("\n❌ Gagal login. Silakan coba lagi.")
            driver_global.quit()
            return
        
        # Tunggu loading selesai setelah login
        debug_html(driver_global.page_source, "./page_now.html")
        
        # Tunggu loading selesai
        loading_success = wait_for_loading_complete(driver_global, timeout=60)
        
        if not loading_success:
            print("⚠️ Loading belum selesai, tetapi melanjutkan...")
        
        # Simpan session setelah login berhasil
        if is_logged_in(driver_global):
            print("\n💾 Menyimpan session ke profil Firefox...")
            save_debug_info(driver_global, "session_saved")
            print("✅ Session berhasil disimpan!")
    
    # Bot loop
    try:
        print("\n🤖 Bot siap digunakan!")
        print("📸 Screenshot disimpan di folder './screenshot-session'")
        print("💡 Tekan Ctrl+C untuk berhenti\n")
        
        while True:
            # Bot loop tanpa screenshot otomatis (hemat resource)
            time.sleep(5)
            if "WhatsApp" in driver_global.title:
                pass
                
    except KeyboardInterrupt:
        print("\n⏹️ Bot dihentikan")
    finally:
        save_debug_info(driver_global, "final_state")
        print(f"📁 Total screenshot: {ITERATION_COUNTER}")
        driver_global.quit()

driver_global = None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Bot dihentikan")
        exit(0)
