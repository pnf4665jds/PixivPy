import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options

s = requests.session()
 # 設定Driver的選項功能，並啟動Headless模式
chromeOptions = Options()  
chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--disable-gpu')
chromeOptions.add_argument('--window-size=1920,1200')
chromeOptions.add_argument('--log-level=3')     # 避免出現Console訊息
driver = webdriver.Chrome(options=chromeOptions)

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

    def processItem(self):
        i = 0
        path = ""
        for item in self.items:
            i = i + 1
            url = "https://www.pixiv.net/artworks/%s" % item
            driver.get(url)
            print("正在處理第%d張圖片" % i)
            try:
                inner_html = wait(driver, 10).until(lambda browser: driver.find_element_by_id("root").find_element_by_xpath(path).get_attribute("innerHTML").strip())
                wait(driver, 10).until(lambda browser: browser.find_element_by_id("root").find_element_by_xpath(path).get_attribute("innerHTML").strip() != inner_html)
                viewNum = driver.find_element_by_id("root").find_element_by_xpath(path).get_attribute("innerHTML")
            except:
                pageNum = pageNum - 1
                print('Time Out, will try again!')    
            else:
                print("瀏覽數:%d" % viewNum)
            pageNum = pageNum + 1


    def start(self):
        self.loginWithSelenium()
        # 等待五秒
        time.sleep(2)
        tag = input("Please input tag: ")
        page = int(input("Please input maximum number of page to search: "))
        self.items = []
        pageNum = 1
        path = "//div/div/div/section/div/ul"
        while (pageNum < (page + 1)):
            url = "https://www.pixiv.net/tags/%s/artworks?p=%d&mode=safe" % (tag, pageNum)
            driver.get(url)
            # 等待10秒來取得動態產生之物件的內容
            # 若超時則重新讀取
            print('正在處理第%d頁' % pageNum)
            try:
                inner_html = wait(driver, 10).until(lambda browser: driver.find_element_by_id("root").find_element_by_xpath(path).get_attribute("innerHTML").strip())
                wait(driver, 10).until(lambda browser: browser.find_element_by_id("root").find_element_by_xpath(path).get_attribute("innerHTML").strip() != inner_html)
                inner_html = driver.find_element_by_id("root").find_element_by_xpath(path).get_attribute("innerHTML")
                pattern = re.compile('href="/artworks/(.*?)"', re.S)
                self.items = set(re.findall(pattern, inner_html))
            except:
                pageNum = pageNum - 1
                print('Time Out, will try again!')    
            else:
                print(self.items)
            pageNum = pageNum + 1
            print('-----------------------------------------------------')
        
        # 關閉Driver
        driver.close()

Pixiv().start()