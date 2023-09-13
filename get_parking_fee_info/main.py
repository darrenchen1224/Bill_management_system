# 載入 selenium 相關模組
from selenium import webdriver

# selenium 4 以上版本，不再 import options ， 改為 import service 和 webdriver_manager :
# 參考 : https://github.com/SergeyPirogov/webdriver_manager
# from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# 連線到 MongoDB 雲端資料庫
from pymongo.mongo_client import MongoClient
import urllib.parse  # 因密碼有 @ ，因此載入 urlib.parse 套件，解析 URL

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PIL import Image   # 用於驗證碼截圖
import os
import easyocr  # 辨識驗證碼
import cv2
import numpy as np 
import time

def cancel_ad_windows():
    while True:
        try:
            # 取消廣告
            # click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-close')))
            time.sleep(1)
            click = driver.find_element(By.CLASS_NAME, 'btn-close')
            click.click()
            print("已取消廣告")
            break
        except:
            print("wait....")

def run(vehicle_info):
    
    # 找到登入頁面
    driver.get("https://parkingfee.pma.gov.taipei/")

    # 取消首次進入的廣告視窗
    cancel_ad_windows()

    # 網頁預設是汽車，因此只要判斷使用者是不是機車即可
    if vehicle_info['vehicle'] == "scooter" :
        # 點選機車
        # vehicle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@for="v2"]')))
        time.sleep(1)
        vehicle = driver.find_element(By.XPATH, '//*[@for="v2"]')
        vehicle.click()
    print("已勾選車種")

    # 找到車牌號碼欄位,並輸入號碼
    # firstnum = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FeeSearchViewModel_PlateNumFront")))
    time.sleep(1)
    firstnum = driver.find_element(By.ID, "FeeSearchViewModel_PlateNumFront")
    firstnum.send_keys(vehicle_info['first_num'])


    # lastnum = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FeeSearchViewModel_PlateNumEnd")))
    time.sleep(1)
    lastnum = driver.find_element(By.ID, "FeeSearchViewModel_PlateNumEnd")
    lastnum.send_keys(vehicle_info['last_num'])

    print("已輸入車牌號碼")

    # 輸入驗證碼
    captcha_result = recognize_captcha()    # 辨識驗證碼
    # code = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FeeSearchViewModel_Captcha")))
    time.sleep(1)
    code = driver.find_element(By.XPATH, '//*[@id="FeeSearchViewModel_Captcha"]')
    code.send_keys(captcha_result)
    print("已輸入驗證碼")

    # 送出車輛資訊
    send_vehicle_info(vehicle_info)


def recognize_captcha() :

    # 驗證碼截圖
    scroll_width = driver.execute_script(
        'return document.documentElement.scrollWidth')
    scroll_height = driver.execute_script(
        'return document.documentElement.scrollHeight')
    driver.set_window_size(scroll_width, scroll_height)

    cwd = os.getcwd()   # 目前路徑
    full_screen_dir = os.path.join(cwd, 'get_parking_fee_info/captcha/')
    full_screen_dir = os.path.join(full_screen_dir,'full_screenshot.jpg') # 全螢幕截圖圖片路徑

    captcha_dir = os.path.join(cwd, 'get_parking_fee_info/captcha/')
    captcha_dir = os.path.join(captcha_dir,'captcha.jpg') # 驗證碼圖片路徑
    
    driver.save_screenshot(full_screen_dir)
    # captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "imgCaptcha")))
    time.sleep(1)
    captcha = driver.find_element(By.ID, "imgCaptcha")
    left = captcha.location['x']
    right = captcha.location['x'] + captcha.size['width']
    top = captcha.location['y']
    bottom = captcha.location['y'] + captcha.size['height']
    img = Image.open(full_screen_dir)
    img = img.crop((left, top, right, bottom))
    img = img.convert("RGB")
    img.save(captcha_dir)
    img.close()
    print("驗證碼截圖")

    # 辨識驗證碼
    img = cv2.imdecode(np.fromfile(captcha_dir, dtype=np.uint8),1) # 因 cv2 無法讀取中文路徑，因此透過 imdecode 讀取圖片路徑
    height, width = img.shape[:2]
    img = cv2.resize(img,(int(1 * width), int(2 * height)), interpolation=cv2.INTER_LINEAR) # 將驗證碼圖片校正，解碼的成功率比較高
    reader = easyocr.Reader(['ch_tra', 'en'])
    captcha_result = reader.readtext(img, detail=0)
    print("captcha : ", captcha_result)
    return captcha_result


# 將車輛資訊送出
def send_vehicle_info(vehicle_info):
    while True:
        try:    # 若登入成功，將停車費資訊儲存至資料庫
            # enterbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/article[2]/div/section[2]/div/form/div/div[5]/button')))
            time.sleep(1)
            enterbutton = driver.find_element(By.XPATH, '//*[@id="main"]/article[2]/div/section[2]/div/form/div/div[5]/button')
            enterbutton.send_keys(Keys.ENTER)
            print("已送出表單")
            check_success = driver.find_element(By.ID,"home-tab")
            save_park_info(vehicle_info)
            break
        except: # 若登入失敗，重新輸入所有資訊
            print("驗證失敗，重新驗證")
            run(vehicle_info)
            break


# 找出停車費資訊，並存到該使用者的資料中
def save_park_info(vehicle_info) :
    parking_fee_container = driver.find_elements(By.XPATH,'//*[@id="feeContainer"]/div[3]')
    for element in parking_fee_container :
        text = str(element.text)
        context = text.replace("條碼繳費", '').replace("智慧支付", "")
        collection.update_one(
            {
                "account" : vehicle_info["account"]
            },
            {
                "$set": {
                    "parking_info" : context
                }
            }
        )
        print("將停車資訊存到資料庫")


if __name__ == '__main__':
    
    # 資料庫連線，並設定 database
    username = urllib.parse.quote_plus('Darren')
    password = urllib.parse.quote_plus('P@ssw0rd1234')
    client = MongoClient(
        "mongodb+srv://%s:%s@mycluster.a0nsuov.mongodb.net/?retryWrites=true&w=majority" % (username, password))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
        
    db = client.account
    collection = db.users

    # 連線 chromedriver
    service = ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options = options, service=service)

    # 找出所有有填車輛資訊的資料
    cursor = collection.find(
        {
            "has_vehicle": True
        }
    )

    # 針對有填寫車輛資訊的資料開始進行爬蟲
    for data in cursor :
        
        # 定義查詢資訊
        vehicle_info = {
            "account" : data["account"],
            "vehicle" : data["vehicle"],
            "first_num" : data["first_num"],
            "last_num" : data["last_num"]
        }

        # 開始爬取車輛資訊
        run(vehicle_info)

    driver.close()
