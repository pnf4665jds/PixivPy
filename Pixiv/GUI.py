import tkinter as tk
import PixivV2
import requests
import threading
import time
from pixivapi import Size
from io import BytesIO
from PIL import ImageTk, Image

large_font = ('Verdana',30)
small_font = ('Verdana', 16)

number = 0
loading = False

class MyGUI:
    safeButtonState = True

    # 初始化
    def __init__(self):
        # 建立Pixiv物件
        self.pixiv = PixivV2.Pixiv()
        # 登入視窗
        self.success = False
        self.loginGUI()
        if not self.success:
            return

        # 建立主視窗和 Frame（把元件變成群組的容器）
        self.window = tk.Tk()
        self.window.geometry('1024x720+0+0')
        # 將元件分為 top/bottom 兩群並加入主視窗
        self.top_frame = tk.Frame(self.window)
        self.top_frame.pack()
        self.bottom_frame = tk.Frame(self.window)
        self.bottom_frame.pack(side=tk.BOTTOM)
        self.left_frame = tk.Frame(self.window)
        self.left_frame.pack(side=tk.LEFT)
        self.right_frame = tk.Frame(self.window)
        self.right_frame.pack(side=tk.RIGHT)
        # 設定輸入欄位
        self.tagLabel = tk.Label(self.bottom_frame, font=large_font, text='Tag: ')
        self.tagLabel.pack(side=tk.LEFT)
        self.tagEntry = tk.Entry(self.bottom_frame, font=large_font, width=10)
        self.tagEntry.pack(side=tk.LEFT)
        # 設定搜尋頁數欄位
        self.pageLabel = tk.Label(self.bottom_frame, font=large_font, text='Page: ')
        self.pageLabel.pack(side=tk.LEFT)
        self.pageEntry = tk.Entry(self.bottom_frame, font=large_font, width=10)
        self.pageEntry.pack(side=tk.LEFT)
        # 過濾模式
        self.safeModeButton = tk.Button(self.bottom_frame, text="Safe", width=16, command=self.toggle)
        self.safeModeButton.pack(pady=5, side=tk.LEFT)
        # 讀取提示Label
        self.loadLabel = tk.Label(self.top_frame, font=large_font, text='')
        self.loadLabel.pack(side=tk.LEFT)
        # 編號與收藏數
        self.keepLabel = tk.Label(self.left_frame, font=large_font, text='收藏數:0')
        self.keepLabel.pack(side=tk.BOTTOM)
        self.idLabel = tk.Label(self.left_frame, font=large_font, text='ID:0')
        self.idLabel.pack(side=tk.BOTTOM)
        self.numLabel = tk.Label(self.left_frame, font=large_font, text='#0')
        self.numLabel.pack(side=tk.BOTTOM)
        # 按鈕
        self.exit_button = tk.Button(self.right_frame, text="Quit", font=small_font, command=self.winClose)  # 離開按鈕
        self.exit_button.pack(side=tk.BOTTOM)
        self.search_button = tk.Button(self.right_frame, text="Search", font=small_font, command=self.search) # 搜尋按鈕
        self.search_button.pack(side=tk.BOTTOM)
        self.next_button = tk.Button(self.right_frame, text="Next", font=small_font, command=lambda: self.next(1)) # 下一張按鈕
        self.next_button.pack(side=tk.BOTTOM)
        self.pre_button = tk.Button(self.right_frame, text="Previous", font=small_font, command=lambda: self.next(-1)) # 上一張按鈕
        self.pre_button.pack(side=tk.BOTTOM)
        self.setButtons(False)
        self.search_button["state"] = "normal"  # 一開始可以按搜尋鈕
        # 圖片展示處
        self.label_image = tk.Label(self.window)
        self.label_image.pack()
        # 開始運行
        self.window.mainloop()      

    # 安全模式開關
    def toggle(self):
        self.safeButtonState = not self.safeButtonState
        if self.safeButtonState:
            self.safeModeButton['text'] = 'Safe'
        else:
            self.safeModeButton['text'] = 'All'

    # 登入用GUI
    def loginGUI(self):
        def winClose():
            loginWin.destroy()

        def tryLogin():
            failLabel['text'] = ''
            self.pixiv.loginWithSelenium(idEntry.get(), passEntry.get())
            self.success = self.pixiv.ifLoginSuccess()
            # 成功登入時關閉視窗，失敗時顯示Fail提示
            if self.success:
                winClose()
            else:
                failLabel['text'] = 'Fail!!'

        loginWin = tk.Tk()
        loginWin.geometry('600x400+100+100')
        # 帳號輸入欄
        idLabel = tk.Label(loginWin, font=large_font, text='User: ')
        idLabel.pack(side=tk.TOP)
        idEntry = tk.Entry(loginWin, font=large_font, width=10)
        idEntry.pack(side=tk.TOP)
        # 密碼輸入欄
        passLabel = tk.Label(loginWin, font=large_font, text='Pass: ')
        passLabel.pack(side=tk.TOP)
        passEntry = tk.Entry(loginWin, font=large_font, width=10, show="*")
        passEntry.pack(side=tk.TOP)
        # 登入按鈕
        login_button = tk.Button(loginWin, text="Login", font=small_font, command=tryLogin) 
        login_button.pack(side=tk.TOP)
        # 離開按鈕
        exit_button = tk.Button(loginWin, text="Quit", font=small_font, command=winClose)
        exit_button.pack(side=tk.TOP)
        # 提示
        failLabel = tk.Label(loginWin, font=large_font, text='')
        failLabel.pack(side=tk.TOP)
        loginWin.mainloop()

    # 設置圖片
    def setImage(self, data, number):
        # 透過url取得圖片
        url = data.image_urls.get(Size.MEDIUM)
        img_headers = {
                'Referer': url,
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/"  
                "537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"}
        response = requests.get(url, headers=img_headers)
        img_data = response.content
        # 將bytes data轉成可顯示的image格式
        self.image = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
        #self.label_image = tk.Label(self.window, image=self.image)
        #self.label_image.pack()
        self.label_image["image"] = self.image
        # 設置圖片相關資料
        self.keepLabel["text"] = '收藏數:%d' % data.total_bookmarks
        self.idLabel["text"] = 'ID:%d' % data.id
        self.numLabel["text"] = '#%d' % number
    
    # 開始search的thread
    def search(self):
        self.pixiv.safeMode = self.safeButtonState
        t = threading.Thread(target=self.process)
        t.start()

    # 開始next的thread
    def next(self, dir):
        t = threading.Thread(target=self.nextImage, args=(dir,))
        t.start()
    
    # 尋找前100的圖
    def process(self):
        global number
        global loading
        #nHen = NHen.NHen(self.entry.get(), self)
        #self.imgs = nHen.getPicInPage(1)
        #self.setImage(self.imgs[1][1])
        loadThread = threading.Thread(target=self.loadingLabel)
        loading = True
        loadThread.start()
        self.setButtons(False)
        try:
            self.pixiv.start(self.tagEntry.get(), int(self.pageEntry.get()))
        except:
            print("pixiv start error")
        #self.pixiv.start(self.entry.get(), 1)
        data = self.pixiv.getImage(0)
        if data == None:
            loading = False
            self.loadLabel["text"] = 'Try again!!'
            self.setButtons(True)
            return
        else:
            self.listSize = self.pixiv.getListSize() 
            self.setImage(data, 1)
            self.setButtons(True)
            self.pre_button["state"] = "disabled"
            number = 0
            loading = False
            self.loadLabel.grid_remove()

    # 切換下一張圖，dir值為1表示往後,-1表示往前
    def nextImage(self, dir):
        global number
        global loading
        loadThread = threading.Thread(target=self.loadingLabel)
        loading = True
        loadThread.start()
        number = number + 1 * dir
        self.setButtons(False)
        data = self.pixiv.getImage(number)
        if data == None:
            loading = False
            self.loadLabel["text"] = 'Try again!!'
            self.setButtons(True)
            return
        else:
            self.setImage(data, number + 1)
            self.setButtons(True)
            loading = False
            self.loadLabel.grid_remove()
             # 防止超出範圍
            if number == 0:
                self.pre_button["state"] = "disabled"
            elif number == self.listSize - 1:
                self.next_button["state"] = "disabled"
    
    # 設定按鈕狀態
    def setButtons(self, enable):
        if enable:
            self.next_button["state"] = "normal"
            self.pre_button["state"] = "normal"
            self.search_button["state"] = "normal"
        else:
            self.next_button["state"] = "disabled"
            self.pre_button["state"] = "disabled"
            self.search_button["state"] = "disabled"
    
    # 簡單的讀取中提示
    def loadingLabel(self):
        global loading
        r = 255
        g = 255
        b = 255
        sign = 1
        self.loadLabel.grid()
        self.loadLabel["text"] = 'Loading!!'
        while loading:
            self.loadLabel.config(foreground='#%02x%02x%02x' % (r, g, b))
            if r == 60 and g == 60 and b == 60:
                sign = -1
            elif r == 255 and g == 255 and b == 255:
                sign = 1
            r = r - 15 * sign
            g = g - 15 * sign
            b = b - 15 * sign
            time.sleep(0.1)
    
    # 關閉視窗
    def winClose(self):
        try:
            PixivV2.mainDriver.close()
        except:
            print("mainDri close err")
        self.window.destroy()

MyGUI()