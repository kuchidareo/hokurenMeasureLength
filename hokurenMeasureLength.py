import tkinter as tk
from tkinter import filedialog
import pathlib
import os
import numpy as np
from PIL import Image, ImageTk
import cv2

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)

        self.master.title("Hokuren Measure Length")
        self.master.state("zoomed")

        self.master.update_idletasks()
        self.winWidth = self.master.winfo_width()
        self.winHeight = self.master.winfo_height()
        self.canvasWidth = int(self.winWidth * 4 / 5)
        self.canvasHeight = int(self.winHeight)

        self.edittingImagePathList = []
        self._temp_list = []

        self.initFrameAndButtonSet()

    def makeDir(self, dirPath):
        self.rinkakuDir = dirPath.parent / "輪郭線"

        if not self.rinkakuDir.exists():
            self.rinkakuDir.mkdir()

    # cv2.imread()を日本語に対応
    def imread(self, path):
        tmp_dir = os.getcwd()
        if len(path.split("/")) > 1:
            file_dir = "/".join(path.split("/")[:-1])
            os.chdir(file_dir)
        tmp_name = "tmp_name"
        os.rename(path.split("/")[-1], tmp_name)
        img = cv2.imread(tmp_name)
        os.rename(tmp_name, path.split("/")[-1])
        os.chdir(tmp_dir)
        return img

    # cv2.imwrite()を日本語に対応
    def imwrite(self, path, img):
        tmp_dir = os.getcwd()
        if len(path.split("/")) > 1:
            file_dir = "/".join(path.split("/")[:-1])
            os.chdir(file_dir)
        tmp_name = "tmp_name.jpg"
        cv2.imwrite(tmp_name, img)
        if os.path.exists(path.split("/")[-1]):  # ファイルが既にあれば削除
            os.remove(path.split("/")[-1])
        os.rename(tmp_name, path.split("/")[-1])
        os.chdir(tmp_dir)


    def initFrameAndButtonSet(self):
        self.imageCanvas = tk.Canvas(
            self.master,
            height = self.winHeight,
            width = self.winWidth * 4 / 5,
            bg = "#c0c0c0"
        )

        operateFrame = tk.Frame(
            self.master,
            height = self.winHeight,
            width = self.winWidth / 5,
            bg = "#c0c0c0"
        )

        self.csvButton = tk.Button(
            operateFrame,
            text = "Click to read CSV",
            height = 10,
            width = 50,
            command = self.getImagePathsFromDir
        )

        self.clearButton = tk.Button(
            operateFrame,
            text = "Clear",
            height = 10,
            width = 50,
            command = self.clearButtonClicked,
            state = tk.DISABLED
        )

        self.processLabel = tk.Label(
            operateFrame,
            height = 10,
            width = 50,
        )


        self.doneButton = tk.Button(
            operateFrame,
            text = "Done",
            height = 10,
            width = 50, 
            command = self.doneButtonClicked,
            state = tk.DISABLED
        )

                
        

        self.imageCanvas.pack(side = tk.LEFT, fill = tk.BOTH)
        operateFrame.pack(side = tk.RIGHT, fill = tk.BOTH)
        self.csvButton.pack(side = tk.TOP, pady = 10,)
        self.processLabel.pack(side = tk.TOP, pady = 10,)
        self.doneButton.pack(side = tk.BOTTOM, pady = 10,)
        self.clearButton.pack(side = tk.BOTTOM, pady = 10,)


    def clearButtonClicked(self):
        print("clear")

    def doneButtonClicked(self):
        print("done")

    def getImagePathsFromDir(self):
        iDir = os.path.expanduser('~/Document/MIJDB')
        dPath = filedialog.askdirectory(initialdir = iDir)

        dPath = pathlib.Path(dPath)
        dPathList = list(dPath.iterdir())

        self.makeDir(dPath)
        self.chooseEdittingImages(dPathList)

    def chooseEdittingImages(self, dPathList):
        # WindowsPath('C:/Users/user/Downloads/AmazonPhotos (1)/
        # 20220217102111_
        # 2511447117498112202153101002440700201351761220019_
        # 5176_1.jpg')

        for path in dPathList:
            imageIndex = path.stem.split("_")[-1]
            if imageIndex in ["1","6"]:
                self.edittingImagePathList.append(path)

        self.imageSet(self.edittingImagePathList[0])

    def openCVToResizedTkData(self, image_bgr):
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)

        ratio = image_pil.width / image_pil.height
        image_pil = image_pil.resize((int(self.canvasHeight*ratio), self.canvasHeight))
        
        resizedImage_tk  = ImageTk.PhotoImage(image_pil)
        return resizedImage_tk

    def imageSet(self, dirPath):
        img = self.imread(str(dirPath))
        img = self.openCVToResizedTkData(img)
        self.imageCanvas.create_image(
            self.canvasWidth / 2,
            self.canvasHeight / 2,
            image = img
        )
        self._temp_list.append(img)
        






if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    app.mainloop()