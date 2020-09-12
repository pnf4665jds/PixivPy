import re
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import traceback
import threading
from multiprocessing.pool import ThreadPool
from pixivapi import Client
from pixivapi import Size
from pathlib import Path

# 登陸地址
loginUrl = 'https://www.pixiv.net/login.php'
# Pixiv帳號密碼
#pixiv_id = 'yen0205'
#password = 'apnf4665jds'
pixiv_id = -1
password = -1

 # 設定Driver的選項功能，並啟動Headless模式
chromeOptions = Options()  
chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--disable-gpu')
chromeOptions.add_argument('--window-size=1920,1200')
chromeOptions.add_argument('--log-level=3')     # 避免出現Console訊息
chromeOptions.add_argument('--ignore-certificate-errors')
chromeOptions.add_argument('--ignore-ssl-errors')
#mainDriver = webdriver.Chrome()
drivers = []        # 儲存所有產生的Driver
mainDriver = webdriver.Chrome(options=chromeOptions)

# 紀錄最高收藏數的圖ID
bestKeepList = []

# 儲存子執行序
threads = []

class Pixiv:
    safeMode = None
    
    # 物件初始化
    def __init__(self):
        mainDriver.get(loginUrl)

    # 利用Web driver模擬登入Pixiv
    def loginWithSelenium(self, id, pw):
        global pixiv_id
        global password
        pixiv_id = id
        password = pw
        fieldGroup = mainDriver.find_element_by_xpath("//div[@class='input-field-group']")
        # 獲取User ID輸入欄
        userNameField = fieldGroup.find_element_by_xpath("//div[@class='input-field']/input[@type='text'][@autocomplete='username']")
        userNameField.clear()
        userNameField.send_keys(pixiv_id)
        # 獲取密碼輸入欄
        passwordField = fieldGroup.find_element_by_xpath("//div[@class='input-field']/input[@type='password'][@autocomplete='current-password']")
        passwordField.clear()
        passwordField.send_keys(password)
        # 獲取提交按鈕
        submitButton = mainDriver.find_element_by_xpath("//div[@id='LoginComponent']/form/button[@type='submit'][@class='signup-form__submit']")
        submitButton.click()

    def ifLoginSuccess(self):
        time.sleep(3)
        return mainDriver.current_url == 'https://www.pixiv.net/'

    # 用於取得一個頁面內所有圖片ID，目前一頁最多60個ID
    def start(self, tag, page):
        global bestKeepList
        bestKeepList.clear()
        # 開始時間
        print("start time: " + str(datetime.datetime.now()))
        items = []          # 儲存這一頁的所有插圖Id
        pageNum = 1         # 從第一頁開始
        toNext = True
        path = "html/body/div/div/div/div/div/div/section/div/ul"       # xPath in html to get illustration id
        errorCount = 0      # 紀錄數據取得失敗的次數，達到三次將退出
        while (pageNum < (page + 1)):
            if toNext:
                if self.safeMode:
                    url = "https://www.pixiv.net/tags/%s/illustrations?p=%d&mode=safe" % (tag, pageNum)
                else:
                    url = "https://www.pixiv.net/tags/%s/illustrations?p=%d" % (tag, pageNum)
                print(url)
                mainDriver.get(url)
                toNext = False
            
            print('正在處理第%d頁' % pageNum)
            try:
                timer = 0
                while True:
                    timer = timer + 1
                    time.sleep(0.5)
                    inner_html = mainDriver.find_element_by_xpath(path).get_attribute("innerHTML")
                    pattern = re.compile('href="/artworks/(.*?)"', re.S)
                    self.items = list(set(re.findall(pattern, inner_html)))
                    if len(self.items) > 0:
                        break
                    elif timer >= 10:
                        raise Exception
            except:
                pageNum = pageNum - 1
                print("超時，將會再嘗試%d次" % (2 - errorCount))
                errorCount = errorCount + 1
            else:
                if len(self.items) > 0:
                    print("ID獲取完成!")
                    #MyThread(self.items, pageNum)     # 建立新的Thread
                    PixApi(self.items, pageNum)
                toNext = True
                errorCount = 0
            # 每五頁執行一次
            if (pageNum % 5) == 0 or pageNum == page:
                print("開始收集每張圖的收藏數!請稍等!")
                self.runThread()
            elif errorCount >= 3:
                self.runThread()
                break
            
            pageNum = pageNum + 1
            print('-----------------------------------------------------')

        print("finish time: " + str(datetime.datetime.now()))
        
        # 關閉Driver
        for driver in drivers:
            driver.close()

        bestKeepList.sort(key=self.takeSecond, reverse=True)
        #print(len(bestKeepList))
        bestKeepList = bestKeepList[:100]   # 保留前一百個
        #print(bestKeepList)
        self.resultClient = Client()
        self.resultClient.login(pixiv_id, password)

    # 執行儲存於threads中的子執行序，並於完成後清除
    def runThread(self):
        # t.join(): 等待所有子執行序執行結束才會繼續跑主執行序
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("清空Thread!")
        threads.clear()

    # 用於排序所使用的compare函式
    def takeSecond(self, element):
        return element[1]

    # 利用Pixiv api取得指定ID的圖片資訊
    def getImage(self, index):
        id = bestKeepList[index][0]
        errorCount = 0
        while errorCount < 3:
            try:
                illuData = self.resultClient.fetch_illustration(id)
                return illuData
            except:
                print("fetch err")
                errorCount = errorCount + 1
                time.sleep(0.5)
        return None
        #illuData.download(directory=Path('D:/123'), size=Size.ORIGINAL)

    # 取得儲存前100名的List之大小
    def getListSize(self):
        return bestKeepList.__len__()

class MyThread:
    # 初始化
    def __init__(self, items, index):
        # Multi-Threading
        print("Page:%d" % index)
        print(len(items))
        self.items = items
        self.threadID = index
        self.threadLocal = threading.local()
        self.driver = self.getDriver()
        drivers.append(self.driver)
        setattr(self.threadLocal, 'driver', self.driver)
        thread = threading.Thread(target=self.processItem, name=("Page%d" % index))
        threads.append(thread)
        
    # 取得driver
    def getDriver(self):
        driver = getattr(self.threadLocal, 'driver', None)
        if driver is None:
            print('None, Create new driver!!')
            driver = webdriver.Chrome(chrome_options=chromeOptions)
            setattr(self.threadLocal, 'driver', driver)
        else:
            print('Get!!')
        return driver
    
    # 取得每一頁最高收藏數的插圖
    def processItem(self):
        bestKeepNum = 0
        bestKeepId = -1
        index = 0
        toNext = True
        path = "//figcaption/div/div/ul/li/a/dl/dd"         # xPath to get favorite number of illustration
        errorCount = 0
        while index < len(self.items):
            if toNext:
                item = self.items[index]
                url = "https://www.pixiv.net/artworks/%s" % item
                self.driver.get(url)
                toNext = False
            print("正在處理第%d頁，第%d張圖片，ID是:%d" % (self.threadID, index + 1, int(item)))
            try:
                timer = 0
                while True:
                    timer = timer + 1
                    time.sleep(0.5)
                    value = self.driver.find_element_by_tag_name('figcaption').find_element_by_xpath(path).get_attribute("innerHTML")
                    if value != None:
                        break
                    elif timer >= 10:
                        raise Exception
            except:
                index = index - 1
                print("超時!!將會再嘗試%d次" % (2 - errorCount))
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

        print("第%d頁完成!\n最高收藏數:%d\nID:%d" % (self.threadID, bestKeepNum, bestKeepId))
        bestKeepList.append((bestKeepId, bestKeepNum))
        print("-----------------------------------------------")

class PixApi:
    # 初始化
    def __init__(self, items, index):
        # Multi-Threading
        print("Page:%d" % index)
        print(len(items))
        self.items = items
        self.threadID = index
        self.threadLocal = threading.local()
        self.client = Client()
        self.illuData = None
        setattr(self.threadLocal, 'client', self.client)
        setattr(self.threadLocal, 'items', self.items)
        self.client.login(pixiv_id, password)
        time.sleep(5)
        thread = threading.Thread(target=self.processItem, name=("Page%d" % index))
        threads.append(thread)
    
    # 取得每一頁最高收藏數的插圖
    def processItem(self):
        index = 0
        errorCount = 0
        item = None
        getVal = False
        while index < len(self.items):
            try:
                timer = 0
                while timer < 3 and index < len(self.items):
                    item = self.items[index]
                    try:
                        self.illuData = self.client.fetch_illustration(int(item))
                    except:
                        pass
                    if self.illuData != None:
                        getVal = True
                        break
                    time.sleep(1)
                    timer = timer + 1
                
            except Exception as E:
                index = index - 1
                print(E)
                errorCount = errorCount + 1  
            if getVal:
                value = int(self.illuData.total_bookmarks)           
                bestKeepList.append((int(item), value))
                getVal = False

            if errorCount >= 3:
                break
            index = index + 1

        print("Thread%d OK!------------------------------------------" % self.threadID)