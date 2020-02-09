import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import traceback

s = requests.session()
 # 設定Driver的選項功能，並啟動Headless模式
chromeOptions = Options()  
chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--disable-gpu')
chromeOptions.add_argument('--window-size=1920,1200')
chromeOptions.add_argument('--log-level=3')     # 避免出現Console訊息
#driver = webdriver.Chrome()
driver = webdriver.Chrome(options=chromeOptions)

# 紀錄最高收藏數的圖ID
bestKeepNum = 0     
bestKeepId = -1

class Pixiv:
    # 初始化
    def __init__(self):
        # 請求封包需要的一些資訊
        # 登陸地址
        self.loginUrl = 'https://www.pixiv.net/login.php'

        #Header資訊
        self.loginHeader = {
            'Host': "www.pixiv.net",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/"  
            "537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
            'Referer': "http://www.pixiv.net/",
            'Content-Type': "application/x-www-form-urlencoded",
            'Connection': "keep-alive"
        }

        self.pixiv_id = 'yen0205'
        self.password = 'apnf4665jds'
        self.return_to = "http://www.pixiv.net/"
        self.postKey = []
    
    # 利用Web driver模擬登入Pixiv
    def loginWithSelenium(self):
        driver.get(self.loginUrl)
        fieldGroup = driver.find_element_by_xpath("//div[@class='input-field-group']")
        # 獲取User ID輸入欄
        userNameField = fieldGroup.find_element_by_xpath("//div[@class='input-field']/input[@type='text'][@autocomplete='username']")
        userNameField.send_keys(self.pixiv_id)
        # 獲取密碼輸入欄
        passwordField = fieldGroup.find_element_by_xpath("//div[@class='input-field']/input[@type='password'][@autocomplete='current-password']")
        passwordField.send_keys(self.password)
        # 獲取提交按鈕
        submitButton = driver.find_element_by_xpath("//div[@id='LoginComponent']/form/button[@type='submit'][@class='signup-form__submit']")
        submitButton.click()

    # 取得頁面的html
    def getPageWithUrl(self, url):
        return s.get(url).text

    def getBestUrl(self):
        return "https://www.pixiv.net/artworks/%s" % bestKeepId

    # 取得每一頁最高觀看數的插圖
    def processItem(self):
        global bestKeepNum
        global bestKeepId
        index = 0
        toNext = True
        #path = "//div/div/div/main/section/div/div/figcaption/div/div/ul/li/dl/dd"       # xPath in html to get view number
        #path = "html/body/div/div/div/div/main/section/div/div/figcaption/div/div/ul/li/a/dl/dd"
        path = "//figcaption/div/div/ul/li/a/dl/dd"
        errorCount = 0
        while index < len(self.items):
            if toNext:
                item = self.items[index]
                url = "https://www.pixiv.net/artworks/%s" % item
                driver.get(url)
                toNext = False
            #print("正在處理第%d張圖片，ID是:%d" % (index + 1, int(item)))
            try:
                timer = 0
                while True:
                    timer = timer + 1
                    time.sleep(0.5)
                    #value = driver.find_element_by_xpath(path).get_attribute("innerHTML")
                    #value = driver.find_element_by_tag_name('figcaption').find_element_by_tag_name('a').find_element_by_tag_name('dd').get_attribute("innerHTML")
                    value = driver.find_element_by_tag_name('figcaption').find_element_by_xpath(path).get_attribute("innerHTML")
                    if value != None:
                        break
                    elif timer == 10:
                        raise Exception
            except:
                index = index - 1
                print("超時，將會再嘗試%d次" % (2 - errorCount))
                errorCount = errorCount + 1  
            else:
                value = int(value.replace(',', ''))
                if value > bestKeepNum:
                        bestKeepNum = value
                        bestKeepId = int(item)
                #print("收藏數取得成功!")
                toNext = True

            if errorCount >= 3:
                break
            index = index + 1


    def start(self):
        self.loginWithSelenium()
        # 等待五秒
        time.sleep(2)
        tag = input("Please input tag: ")
        page = int(input("Please input maximum number of page to search: "))
        self.items = []
        pageNum = 1
        toNext = True
        path = "html/body/div/div/div/div/section/div/ul"       # xPath in html to get illustration id
        errorCount = 0
        while (pageNum < (page + 1)):
            if toNext:
                url = "https://www.pixiv.net/tags/%s/artworks?p=%d&mode=safe" % (tag, pageNum)
                driver.get(url)
                toNext = False
            # 等待10秒來取得動態產生之物件的內容
            # 若超時則重新讀取
            print('正在處理第%d頁' % pageNum)
            try:
                #inner_html = wait(driver, 10).until(lambda browser: driver.find_element_by_xpath(path).get_attribute("innerHTML").strip())
                #wait(driver, 10).until(lambda browser: driver.find_element_by_xpath(path).get_attribute("innerHTML").strip() != inner_html)
                timer = 0
                while True:
                    timer = timer + 1
                    time.sleep(0.5)
                    inner_html = driver.find_element_by_xpath(path).get_attribute("innerHTML")
                    pattern = re.compile('href="/artworks/(.*?)"', re.S)
                    self.items = list(set(re.findall(pattern, inner_html)))
                    if len(self.items) > 55:
                        break
                    elif timer == 10:
                        raise Exception
            except:
                pageNum = pageNum - 1
                print("超時，將會再嘗試%d次" % (2 - errorCount))
                errorCount = errorCount + 1
            else:
                #print(self.items)
                print("ID獲取完成!")
                self.processItem()
                toNext = True
                errorCount = 0
            if errorCount >= 3:
                break

            pageNum = pageNum + 1
            print('-----------------------------------------------------')
        
        print("結果:\nID:%d\n收藏數:%d" % (bestKeepId, bestKeepNum))
        # 關閉Driver
        driver.close()

Pixiv().start()