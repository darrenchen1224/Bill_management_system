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
  

def click_ad() :
    # 取消廣告視窗
    while True:
        try:
            # 取消廣告
            click = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popupsModal"]/div/div/div[1]/div[1]/button')))
            click.click()
            print("已取消廣告")
            break
        except:
            print("wait....")


def enter_vehicle_info(vehicle_info):

    # 網頁預設是汽車，因此只要判斷使用者是不是機車即可
    if vehicle_info['vehicle'] == "scooter" :
        # 點選機車
        vehicle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@for="v2"]')))
        vehicle.click()
    print("已勾選車種")

    # 輸入車牌前碼
    firstnum = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FeeSearchViewModel_PlateNumFront")))
    firstnum.send_keys(vehicle_info['first_num'])
    print("已輸入車牌前碼")

    # 輸入車牌後碼
    lastnum = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FeeSearchViewModel_PlateNumEnd")))
    lastnum.send_keys(vehicle_info['last_num'])
    print("已輸入車牌後碼")

    # 輸入驗證碼
    enter_captcha()


def enter_captcha() :
    captcha_result = recognize_captcha()    # 辨識驗證碼
    code = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FeeSearchViewModel_Captcha")))
    code.send_keys(captcha_result)
    print("已輸入驗證碼")


def recognize_captcha() :

    # 驗證碼截圖
    scroll_width = driver.execute_script(
        'return document.documentElement.scrollWidth')
    scroll_height = driver.execute_script(
        'return document.documentElement.scrollHeight')
    driver.set_window_size(scroll_width, scroll_height)
    driver.save_screenshot('./captcha/full_screenshot.jpg')
    captcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "imgCaptcha")))
    left = captcha.location['x']
    right = captcha.location['x'] + captcha.size['width']
    top = captcha.location['y']
    bottom = captcha.location['y'] + captcha.size['height']
    img = Image.open('./captcha/full_screenshot.jpg')
    img = img.crop((left, top, right, bottom))
    img = img.convert("RGB")
    img.save('./captcha/captcha.jpg')
    print("驗證碼截圖")

    # 辨識驗證碼
    cwd = os.getcwd()   # 目前路徑
    _dir = os.path.join(cwd, 'captcha/')
    _dir = os.path.join(_dir,'captcha.jpg') # 驗證碼圖片路徑
    img = cv2.imdecode(np.fromfile(_dir, dtype=np.uint8),1) # 因 cv2 無法讀取中文路徑，因此透過 imdecode 讀取圖片路徑
    reader = easyocr.Reader(['ch_tra', 'en'])
    captcha_result = reader.readtext(img, detail=0)
    print("captcha", captcha_result)
    print("辨識驗證碼")
    return captcha_result


# 將車輛資訊送出
def send_vehicle_info(account):
    while True:
        try:    # 若登入成功，將停車費資訊儲存至資料庫
            enterbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/article[2]/div/section[2]/div/form/div/div[5]/button')))
            enterbutton.send_keys(Keys.ENTER)
            print("已送出表單")
            save_park_info(account)
            break
        except: # 若登入失敗，重新辨識驗證碼
            print("recognize fail, recognize again...")
            refresh_capcha = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/article[2]/div/section[2]/div/form/div/div[3]/div/div[1]/a[2]/img')))
            refresh_capcha.click()


# 找出停車費資訊，並存到資料庫
def save_park_info(account) :
    parking_fee_container = driver.find_elements(By.XPATH,'//*[@id="feeContainer"]/div[3]')
    for element in parking_fee_container :
        text = str(element.text)
        context = text.replace("條碼繳費", '').replace("智慧支付", "")
        collection.update_one(
            {
                "account" : account
            },
            {
                "set": {
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
    driver = webdriver.Chrome(options = options, service = service)

    # 從資料庫取出有輸入車資訊的使用者
    cursor = collection.find(
        {
            "has_vehicle" : True
        }
    )
    vehicle_info = {}
    for data in cursor :
        print(data)
        account = data["account"]
        vehicle_info = {
            "vehicle" : data["vehicle"],
            "first_num" : data["first_num"],
            "last_num" : data["last_num"]
        }

        # 找到登入頁面
        driver.get("https://parkingfee.pma.gov.taipei/")

        # 點擊取消廣告
        click_ad()

        # 輸入車輛資訊
        enter_vehicle_info(vehicle_info)

        # 送出車輛資訊，並將停車費資訊更新至對應的 account 的資料中
        send_vehicle_info(account)

        driver.close()