import urllib
import urllib.request
import re
import tkinter
import http.cookiejar

class NHen:
    # constructor
    def __init__(self, tag):
        self.tagUrl = "https://nhentai.net/search/?q=" + tag  # nHen url for tag
        self.baseUrl = "https://nhentai.net/g/"     # nHen url for each comic
        self.cookie = http.cookiejar.LWPCookieJar()
        self.cookieHandler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.cookieHandler)

    def getPicInPage(self, page):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}     # add headers to avoid 403:forbidden error
        self.tagUrl += "&page=%d" % page           # set target page
        request = urllib.request.Request(self.tagUrl, headers=headers)   # make a request data
        response = self.opener.open(request)    # get response for the request
        content = response.read().decode('UTF-8')   # get html
        pattern = re.compile('href="/g/(.*?)/" | data-src="(.*?(jpg|png))"', re.S)  # regex for god's language and preview picture
        items = re.findall(pattern, content)    # find all god's language and store in items list
        #for item in items:
         #   print(item)
        return items