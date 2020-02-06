import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait

s = requests.session()
driver = webdriver.Chrome()

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

    # 獲取此次session的post_key
    def getPostKeyAndCookie(self):
        loginHtml = s.get(self.loginUrl)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">', re.S)
        result = re.search(pattern, loginHtml.text)
        self.postKey = result.group(1)
        loginData = {"pixiv_id": self.pixiv_id, "password": self.password, 'post_key': self.postKey, 'return_to': self.return_to} 
        s.post(self.loginUrl, data = loginData, headers = self.loginHeader)

    # 取得頁面的html
    def getPageWithUrl(self, url):
        return s.get(url).text

    def start(self):
        self.tag = input("Please input tag: ")
        self.getPostKeyAndCookie()

        for pageNum in range(1, 2):
            url = "https://www.pixiv.net/tags/%s/artworks?p=%d" % (self.tag, pageNum)
            #pageHtml = self.getPageWithUrl(url)
            #pageSoup = BeautifulSoup(pageHtml, 'lxml')
            #imgItemsResult = pageSoup.find_all("ul")
            driver.get(url)
            #content = driver.find_element_by_id('root')
            #n = content.get_property('outerHTML')
            #print(n)
            #n2 = content.get_attribute('clientHeight')
            #print(n2)
            inner_html = wait(driver, 10).until(lambda browser: driver.find_element_by_id("root").get_attribute("innerHTML").strip())
            wait(driver, 10).until(lambda browser: browser.find_element_by_id("root").get_attribute("innerHTML").strip() != inner_html)
            inner_html = driver.find_element_by_id("root").get_attribute("innerHTML")
            pattern = re.compile('href="/artworks/(.*?)"', re.S)
            items = re.findall(pattern, inner_html)
            for item in items:
                print(item)

Pixiv().start()