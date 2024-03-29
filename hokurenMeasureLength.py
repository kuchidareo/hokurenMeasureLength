import tkinter as tk
from tkinter import filedialog
import pathlib
import os
import numpy as np
from PIL import Image, ImageTk
import cv2
import csv
import datetime
from memory_profiler import profile

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
        self._temp_image_file = ""

        self.canvasOriImage = ""
        self.onlyLineImage = ""
        self.tempImagePlusCircle = ""
        self.tempImage = ""

        self.mode = "selectCsv"
        self.isLineDrawn = False
        self.isPlotted = False

        self.pointOnLineList = []
        self.resizeOrder = 1

        self.processCount = 0
        self.date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        self.LINE_COLOR = (75, 184, 86)
        self.POINT_COLOR = (163, 106, 1)
        self.TEXT_COLOR = (71, 60, 0)
        self.WHITE_COLOR = (220, 220, 220)
        self.RED_COLOR = (160, 170, 247)

        self.startX = 0
        self.startY = 0
        self.nowX = 0
        self.nowY = 0
        self.endX = 0
        self.endY = 0
        self.beginX = 0
        self.beginY = 0
        self.finalX = 0
        self.finalY = 0

        self.initFrameAndButtonSet()

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
            text = "Click to load Images",
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
        if self.mode == "drawLine":
            self.clearDrawLine()
        elif self.mode == "plotting":
            if self.isPlotted == False:
                self.clearDrawLine()
            else:
                self.isPlotted = False
                self.doneButton.configure(state = tk.DISABLED)
                self.initEditImages()
                self.opencvImgDisplay(self.onlyLineImage)

    def clearDrawLine(self):
        self.mode = "drawLine"
        self.initEditImages()
        self.opencvImgDisplay(self.canvasOriImage)
        self.isLineDrawn = False

        self.clearButton.configure(state = tk.DISABLED)
        self.doneButton.configure(state = tk.DISABLED)


    def doneButtonClicked(self):
        if self.mode == "plotting":
            self.distanseListToCsv(self.distanseList)

            self.mode = "drawLine"
            self.processCount += 1
            self.clearButton.configure(state = tk.DISABLED)
            self.doneButton.configure(state = tk.DISABLED)
            self.imageSet(self.edittingImagePathList[self.processCount])


    def distanseListToCsv(self, list):
        with open(self.csvName, "a",  newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([self.edittingImagePathList[self.processCount].stem] + list)


    def getImagePathsFromDir(self):
        iDir = os.path.expanduser('~/Document/MIJDB')
        dPath = filedialog.askdirectory(initialdir = iDir)

        dPath = pathlib.Path(dPath)
        dPathList = list(dPath.iterdir())

        self.chooseEdittingImages(dPathList)


    def chooseEdittingImages(self, dPathList):
        # WindowsPath('C:/Users/user/Downloads/AmazonPhotos (1)/
        # 20220217102111_
        # 2511447117498112202153101002440700201351761220019_
        # 5176_1.jpg')

        for path in dPathList:
            imageIndex = path.stem.split("_")[-1]
            if imageIndex in ["3","6"]:
                self.edittingImagePathList.append(path)

        self.csvName = str(self.edittingImagePathList[0].parents[1]) + "/" + str(self.date) + "_DistanceData.csv"
        self.imageSet(self.edittingImagePathList[0])


    def initEditImages(self):
        if self.mode == "drawLine":
            self.onlyLineImage = self.canvasOriImage.copy()
            self.tempImagePlusCircle = self.canvasOriImage.copy()
            self.tempImage = self.tempImagePlusCircle.copy()
        elif self.mode == "plotting":
            self.tempImagePlusCircle = self.onlyLineImage.copy()
            self.tempImage = self.onlyLineImage.copy()
            self.distanseList = []
            self.pointOnLineList = []


    def createCanvasImage(self, img, width, height):
        # 背景となるCanvasサイズの黒画像
        back = np.zeros((height, width, 3), dtype = np.uint8)
        pil_back = Image.fromarray(back)
        pil_back = pil_back.convert("RGBA")

        scaledImage, isWide = self.scaleImageToBox(img, width, height)
        pil_image = Image.fromarray(scaledImage)
        pil_image = pil_image.convert("RGBA")

        if isWide:
            x = (self.canvasWidth - pil_image.width) / 2
            y = 0
        else:
            x = 0
            y = (self.canvasHeight - pil_image.height) / 2
        location = (int(x), int(y))

        pil_temp = Image.new("RGBA", pil_back.size, (255, 255, 255, 0))
        pil_temp.paste(pil_image, location, pil_image)
        result_image = Image.alpha_composite(pil_back, pil_temp)

        return cv2.cvtColor(np.asarray(result_image), cv2.COLOR_RGBA2BGRA)


    def scaleImageToBox(self, img, width, height):
        isWide = False
        h, w = img.shape[:2]
        aspect = w / h
        if width / height >= aspect:
            nh = height
            nw = round(nh * aspect)
            isWide = True
        else:
            nw = width
            nh = round(nw / aspect)
        
        self.resizeOrder = nw / w
        dst = cv2.resize(img, dsize=(nw, nh))
        dst = cv2.cvtColor(dst, cv2.COLOR_BGRA2RGBA)

        return dst, isWide


    def openCVToTkData(self, image_bgr):
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk  = ImageTk.PhotoImage(image_pil)
        return image_tk


    def imageSet(self, dirPath):
        img = self.imread(str(dirPath))
        self.canvasOriImage = self.createCanvasImage(img, self.canvasWidth, self.canvasHeight)
        img = self.openCVToTkData(self.canvasOriImage)
        self.imageCanvas.create_image(
            self.canvasWidth / 2,
            self.canvasHeight / 2,
            image = img
        )
        self._temp_image_file = img

        self.csvButton.configure(state = tk.DISABLED)

        self.mode = "drawLine"
        self.initEditImages()

        self.imageCanvas.bind('<ButtonPress-1>', self.mouseDown)
        self.imageCanvas.bind('<B1-Motion>', self.mouseMove)
        self.imageCanvas.bind('<ButtonRelease-1>', self.mouseUp)


    def calculateExtendedLinePoint(self, startX, startY, endX, endY):
        if endX != startX : 
            slope = (endY - startY) / (endX - startX)
            x1 = 0
            y1 = startY - slope * (startX - x1)

            x2 = self.canvasWidth
            y2 = endY - slope * (endX - x2)

            if y1 == y2:
                y2 += 1

        else:
            x1 = startX
            y1 = 0

            x2 = startX
            y2 = self.canvasHeight

        return int(x1), int(y1), int(x2), int(y2)


    def opencvImgDisplay(self, img):
        img = self.openCVToTkData(img)

        self.imageCanvas.create_image(
            self.canvasWidth / 2,
            self.canvasHeight / 2,
            image = img
        )

        self._temp_image_file = img

    def mouseDown(self, event):
        if self.mode == "drawLine":
            self.drawLineMouseDown(event)
        elif self.mode == "plotting":
            self.plottingMouseDown(event)

    def mouseMove(self, event):
        if self.mode == "drawLine":
            self.drawLineMouseMove(event)

    def mouseUp(self, event):
        if self.mode == "drawLine":
            self.drawLineMouseUp(event)
            self.isLineDrawn = False
            self.mode = "plotting"
            self.initEditImages()
        

    def drawLineMouseDown(self, event):
        if self.isLineDrawn == True:
            return

        self.startX = event.x
        self.startY = event.y

        cv2.circle(
            self.tempImagePlusCircle,
            (self.startX, self.startY),
            7,
            self.POINT_COLOR,
            thickness = -1
        )


    def drawLineMouseMove(self, event):
        if self.isLineDrawn == True:
            return

        self.nowX = event.x
        self.nowY = event.y

        beginX, beginY, finalX, finalY = \
             self.calculateExtendedLinePoint(self.startX, self.startY, self.nowX, self.nowY) 

        cv2.line(
            self.tempImage,
            (beginX, beginY),
            (finalX, finalY),
            self.LINE_COLOR,
            5
        )

        self.opencvImgDisplay(self.tempImage)
        self.tempImage = self.tempImagePlusCircle.copy()


    def drawLineMouseUp(self, event):
        if self.isLineDrawn == True:
            return

        self.endX = event.x
        self.endY = event.y

        self.beginX, self.beginY, self.finalX, self.finalY = \
             self.calculateExtendedLinePoint(self.startX, self.startY, self.endX, self.endY) 

        cv2.line(
            self.onlyLineImage,
            (self.beginX, self.beginY),
            (self.finalX, self.finalY),
            self.LINE_COLOR,
            5
        )

        self.opencvImgDisplay(self.onlyLineImage)
        
        self.clearButton.configure(state = tk.NORMAL)
        self.isLineDrawn = True


    # a = 1 で固定して計算している
    def calculateMinDistancePoint(self, b, c, x, y):
        hx = (b**2*x - b*y - c) / (1 + b**2)
        hy = (y - b*x - b*c) / (1 + b**2)

        return [int(hx), int(hy)]

    def calculateCoefficient(self, x1, y1, x2, y2):
        b = (x1 - x2) / (y2 - y1)
        c = (x2*y1 - x1*y2) / (y2 - y1)

        return b, c


    def plottingMouseDown(self, event):
        x = event.x
        y = event.y

        b, c = self.calculateCoefficient(self.beginX, self.beginY, self.finalX, self.finalY)
        pointOnLine = self.calculateMinDistancePoint(b, c, x, y)

        cv2.circle(
            self.tempImagePlusCircle,
            (pointOnLine[0], pointOnLine[1]),
            7,
            self.POINT_COLOR,
            thickness = -1
        )

        self.isPlotted = True
        self.pointOnLineList.append(pointOnLine)
        self.displayDistanceBetweenPoint(self.pointOnLineList)

        if len(self.pointOnLineList) >= 2:
            self.doneButton.configure(state = tk.NORMAL)


    def displayDistanceBetweenPoint(self, pointList):
        sortedList = np.array(sorted(pointList))
        if len(sortedList) == 1:
            self.opencvImgDisplay(self.tempImagePlusCircle)
            return

        self.tempImage = self.tempImagePlusCircle.copy()
        self.distanseList = []

        for i in range(len(sortedList) - 1):
            distance = (np.linalg.norm(sortedList[i+1] - sortedList[i]) / self.resizeOrder).astype(int)
            centerPoint = ((sortedList[i+1] + sortedList[i]) / 2).astype(int)
            if i % 2 == 1:
                position = [centerPoint[0]-20, centerPoint[1]-40]
                color = self.RED_COLOR
            else:
                position = [centerPoint[0]-20, centerPoint[1]+40]
                color = self.WHITE_COLOR

            self.writeTextAndRectangle(str(distance), position, color)
            
            self.distanseList.append(distance)
            self.opencvImgDisplay(self.tempImage)

    def writeTextAndRectangle(self, distance, position, color):
        cv2.rectangle(
            self.tempImage,
            (position[0]-10, position[1]-30),
            (position[0]+70, position[1]+10),
            color,
            -1,
            cv2.LINE_4
        )

        cv2.putText(
            self.tempImage,
            str(distance),
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            self.TEXT_COLOR,
            3,
            cv2.LINE_4
        )



if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    app.mainloop()