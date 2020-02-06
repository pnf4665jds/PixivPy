import urllib
import urllib.request
import urllib.error
import http.cookiejar
import re
import os
import time

class Pixiv:
    #### 初始化 ####
    def __init__(self):
        # 請求封包需要的一些資訊
        # 登陸地址
        self.loginURL = 'https://www.pixiv.net/login.php'

        #Header資訊
        self.loginHeader = {
            'Host': "www.pixiv.net",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/"  
            "537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
            'Referer': "http://www.pixiv.net/",
            'Content-Type': "application/x-www-form-urlencoded",
            'Connection': "keep-alive"
        }

        # 包括使用者名稱、密碼等表單資訊
        self.postData = urllib.parse.urlencode({
            'mode': 'login',
            'return_to': '/',
            'pixiv_id': 'yen0205',
            'pass': 'apnf4665jds',
            'skip': '1'})

        # cookie資訊，伺服器用來識別使用者身份
        # 獲取本地cookie資訊，構建一個包含cookie資訊的opener
        self.cookie = http.cookiejar.LWPCookieJar()
        self.cookieHandler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.cookieHandler)
    
    #### 模擬登陸 ####
    def get_first_page(self):
        # 向伺服器發起請求，請求封包內容包括：URL，Header，表單；請求方式為post
        request = urllib.request.Request(self.loginURL, self.postData, self.loginHeader)
        # 用我們新建的包含cookie資訊的opener開啟，並返回伺服器回應的封包
        response = self.opener.open(request)
        # 內容讀取，並以UTF-8解碼
        content = response.read().decode('utf-8')
        print(u'回應程式碼：%s' % response.getcode())

        return content

    #### 排行榜資訊獲取 ####
    def get_rank_list(self):
        # 進入dailyRank介面
        rank_url = 'http://www.pixiv.net/ranking.php?mode=daily&content=illust'
        request = urllib.request.Request(rank_url)
        response = self.opener.open(request)
        content = response.read().decode('UTF-8')
        print(response.getcode())
        # 利用正規表示式，找到dailyRank介面內的作品資訊（可以儲存為.txt說明用）
        pattern = re.compile('<section.*?data-rank-text="(.*?)" data-title="(.*?)" '  
        'data-user-name="(.*?)" data-date="(.*?)".*?data-id="(.*?)"', re.S)
        # findall返回一個包含5元組的列表
        items = re.findall(pattern, content)
        # 可以列印出來看看
        # for item in items:
        #    print(item[0], item[1], item[2], item[3], item[4])
        print(u"已經獲得排名、名稱、作者、時間、ID資訊O(∩_∩)O哈！")
        return items

    #### 透過關鍵字搜尋 ####
    def get_keyword_list(self, keyword):
        # 進入依輸入的關鍵字找到的介面
        keyword_url = 'https://www.pixiv.net/tags/%s/illustrations?mode=safe' % keyword
        request = urllib.request.Request(keyword_url)
        response = self.opener.open(request)
        content = response.read().decode('UTF-8')
        print(response.getcode())
        pattern = re.compile('href="(.*?)"', re.S)
        items = re.findall(pattern, content)
        for item in items:
            print(item[0])
        return items

    #### 每幅圖片所在頁面的地址獲取 ####
    def get_img_page(self, pageType, optionVal = None):
        # 每幅圖片所在頁面地址 = 基地址   圖片id（這是作者的圖片展示地址）
        base_url = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='
        # 從rank介面獲取到的id資訊派上用場了
        if pageType == 1:
            illust_id = [item[4] for item in self.get_rank_list()]
        elif (pageType == 2) & (optionVal != ""):
            self.get_keyword_list(optionVal)
            #illust_id = [item[4] for item in self.get_keyword_list(optionVal)]
        # 用一個列表儲存所有的頁面地址
        #img_pages = [base_url + str(i) for i in illust_id]
        return []
        #return img_pages

    #### 圖片地址獲取 ####
    def get_img_urls(self, img_pages):
        # 儲存所有圖片url的列表
        img_urls = []
        # 遍歷所有illust_id介面,前100名
        for index, url in enumerate(img_pages[:10]):
            print(u"正在進入第%d名插畫介面" % (index + 1))
            request = urllib.request.Request(url)
            response = self.opener.open(request)
            content = response.read().decode('UTF-8')
            # 查詢原畫地址,不同瀏覽器獲得的HTML有差異，以CHROME為準
            # 插畫的話，直接獲得原圖；如果是漫畫，則獲取縮圖
            try:
                pattern = re.compile('"regular":"(.*?)"', re.S)
                #pattern = re.compile('<img alt.*?data-src="(.*?)"', re.S)
                img = re.search(pattern, content)
                print(img.group(1))
            except AttributeError:
                pattern = re.compile('<div class="multiple.*?src="(.*?)"', re.S)
                img = re.search(pattern, content)
                print(img.group(1))

            img_urls.append(img.group(1))

        return img_urls

    #### 建立儲存目錄 ####
    def make_dir(self):
        # 獲取格式化時間，提取年月日作為目錄名稱
        y_m_d = time.localtime()
        path = 'D:/%s_%s_%s' % (str(y_m_d[0]), str(y_m_d[1]), str(y_m_d[2]))
        is_exist = os.path.exists(path)
        if not is_exist:
            os.makedirs(path)
            print(u"建立目錄成功！")
        else:
            print(u"目錄已經存在！")

        return path
    
    #### 儲存圖片 ####
    def save_img_data(self, urls, pages, path):
        for i, img_url in enumerate(urls):
            filename = path + '/' + str(i + 1) + '.jpg'
            # 裡面的Referer很重要哦，不然伺服器會拒絕訪問，也就獲取不到原圖資料
            # 之前沒有管Referer，直接拋給我403
            # 伺服器會檢查Referer，來判斷是否對這個請求做響應；我們要儘可能模仿正常上網行為。
            # 這裡的Referer就是我們之前獲取到的頁面地址
            img_headers = {
                'Referer': pages[i],
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/"  
                "537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"}
            img_request = urllib.request.Request(img_url, headers = img_headers)
            img_response = self.opener.open(img_request)
            print(img_response.getcode())
            data = img_response.read()
            # input = raw_input()
            # 儲存圖片到指定目錄
            if img_response.getcode() == 200:
                with open(filename, 'wb') as f:
                    f.write(data)
            print(u"儲存第%d張圖片中" % (i + 1))
    
    #### 儲存圖片相關資訊 ####
    def save_info(self, items, path):
        # 記錄前100名的資訊
        filename = path + '/info.txt'
        infos = u'前100名資訊:\n'
        for item in items[:100]:
            infos  = u'-----------第%s------------\n' % item[0]
            infos  = u'Name:%s\nAuthor:%s\nID:%s\n' % (item[1], item[2], item[4])
            with open(filename, 'w') as f:
                f.write(infos.encode('UTF-8'))

# Main
pixiv = Pixiv()
path = pixiv.make_dir()
pages = pixiv.get_img_page(2, "pokemon")
urls = pixiv.get_img_urls(pages)
pixiv.save_img_data(urls, pages, path)

