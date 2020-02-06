import tkinter as tk
import NHen
import requests
from io import BytesIO
from PIL import ImageTk, Image

large_font = ('Verdana',30)

class MyGUI:
    def __init__(self):
        # 建立主視窗和 Frame（把元件變成群組的容器）
        self.window = tk.Tk()
        self.window.geometry('1920x1080')
        # 將元件分為 top/bottom 兩群並加入主視窗
        self.top_frame = tk.Frame(self.window)
        self.top_frame.pack()
        self.bottom_frame = tk.Frame(self.window)
        self.bottom_frame.pack(side=tk.BOTTOM)
        # 設定輸入欄位
        self.label = tk.Label(self.bottom_frame, font=large_font, text='Tag: ')
        self.label.pack(side=tk.LEFT)
        self.entry = tk.Entry(self.bottom_frame, font=large_font)
        self.entry.bind('<Return>', self.search)    # 輸入Enter後執行search function
        self.entry.pack(side=tk.LEFT)
        self.exit_button = tk.Button(self.bottom_frame, text="Quit", font=large_font, command=self.window.destroy)  # 離開按鈕
        self.exit_button.pack(side=tk.RIGHT)
        # 開始運行
        self.window.mainloop()      

    def setImage(self, url):
        # 透過url取得圖片
        response = requests.get(url)
        img_data = response.content
        # 將bytes data轉成可顯示的image格式
        self.image = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
        self.label_image = tk.Label(self.window, image=self.image)
        self.label_image.pack()
    
    def search(self, event):
        nHen = NHen.NHen(self.entry.get(), self)
        self.imgs = nHen.getPicInPage(1)
        self.setImage(self.imgs[1][1])


MyGUI()