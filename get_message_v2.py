import os
import json
import time
import pytz
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Giữ nguyên các hàm cũ của công ty (để đảm bảo tính tương thích)
from get_message import get_gsclient, SPREADSHEET_URL, save_screenshot, create_worksheet, get_messages, open_chat_by_search, get_all_groups, local_tz

def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.page_load_strategy = "eager"
    
    # Cấu hình để tự động nhận diện version Chrome
    driver = uc.Chrome(
        options=options,
        use_subprocess=True,
        driver_executable_path=None # Để None để nó tự tải bản tương thích
    )
    return driver
def login():
    driver = get_driver()
    driver.get("https://teams.microsoft.com/")
    time.sleep(5)

    try:
        print("⏳ Đang tiến hành nạp Cookies để bypass qua màn hình MFA...")
        
        if not os.path.exists("teams_cookies.json"):
            print("❌ Không tìm thấy file teams_cookies.json!")
            driver.quit()
            return None
            
        with open("teams_cookies.json", "r") as f:
            cookies = json.load(f)
            
        for cookie in cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                del cookie['sameSite']
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)
            
        print("🔄 Cookies đã nạp thành công! F5 lại trang...")
        driver.refresh()
        time.sleep(15)
        
        if "teams.microsoft.com" in driver.current_url:
            print("✅ Đăng nhập bằng Cookie thành công!")
            return driver
        else:
            print("⚠️ Chưa vào được Teams, Cookie có thể đã hết hạn.")
            return driver

    except Exception as e:
        save_screenshot(driver, "login_cookie_error.png")
        print("❌ Lỗi nạp Cookie:", e)
        driver.quit()
        return None

if __name__ == "__main__":
    driver = login()
    if driver:
        group_names = get_all_groups(driver)
        for group in group_names:
            try:
                print(f"\n===== {group} =====")
                create_worksheet(group)
                if open_chat_by_search(driver, group):
                    get_messages(driver, group)
                time.sleep(3)
            except Exception as e:
                print("Skip:", group, e)
        driver.quit()
        print("✅ DONE")