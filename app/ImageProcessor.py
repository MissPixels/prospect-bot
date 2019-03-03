import os
import datetime
import urllib
import numpy as np
import cv2
from PIL import Image

from app.Base import Base
from app.utils import helpers


class ImageProcessor(Base):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        config = helpers.getConfig()
        self.grabCutRectRatio = float(config["ImageProcessor"]["GrabCutRectRatio"])
        self.grabCutIterCount = int(config["ImageProcessor"]["GrabCutIterCount"])
        self.originalImagePath = config["Files"]["OriginalImagePath"]
        self.colorizedImagePath = config["Files"]["ColorizedImagePath"]
        self.pixelSortedImagePath = config["Files"]["PixelSortedImagePath"]
        self.finalImagePath = config["Files"]["FinalImagePath"]
        self.token = "{}_{}".format(
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            helpers.getRandomToken(),
        )
        self.log("\n* ImageProcessor initialized")
        self.log("Grab Cut rect ratio\t\t{}".format(self.grabCutRectRatio))
        self.log("Grab Cut iteration count\t{}".format(self.grabCutIterCount))
        self.log("Colorized images path\t\t{}".format(self.colorizedImagePath))
        self.log("Pixel sorted images path\t{}".format(self.pixelSortedImagePath))
        self.log("Final images path\t\t{}".format(self.finalImagePath))

    def colorizeImage(self, imageUrl, currentColor):
        self.log("Processing image {}".format(imageUrl))
        content = urllib.request.urlopen(imageUrl).read()
        nparr = np.fromstring(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        # Crop out watermark
        height, width = img.shape[:2]
        img = img[0:height, 40 : width - 40, :]
        methods = {"grabCut": self.grabCut, "contours": self.contours}
        # Save original image
        filename = "original_{}.png".format(self.token)
        originalImage = Image.fromarray(np.uint8(img))
        originalImage.save(helpers.getFilePath(filename, path=self.originalImagePath))
        filenames = [filename]
        for method in methods:
            res = methods[method](img, currentColor)
            filename = "colorized_{}_{}.png".format(method, self.token)
            res.save(helpers.getFilePath(filename, path=self.colorizedImagePath))
            filenames.append(filename)
        self.log("Done processing image")
        return filenames

    def grabCut(self, img, currentColor):
        height, width = img.shape[:2]
        rect_ratio = float(self.grabCutRectRatio)
        iterCount = int(self.grabCutIterCount)

        # Prepare GrabCut
        rect_width = int(width * rect_ratio)
        rect_height = int(height * rect_ratio)
        rect_x = int((width - rect_width) / 2)
        rect_y = int((height - rect_height) / 2)
        rect = (rect_x, rect_y, rect_width, rect_height)
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        # Do GrabCut
        cv2.grabCut(
            img, mask, rect, bgdModel, fgdModel, iterCount, cv2.GC_INIT_WITH_RECT
        )
        # Extract mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
        img1 = img * mask2[:, :, np.newaxis]
        background = img - img1
        # Make RGBA mask
        shape_y, shape_x, shape_z = background.shape
        alpha_step = 255 / shape_y
        mask_rgba = np.ones((shape_y, shape_x, 4))
        mask_rgba[:, :, :-1] = background
        mask_rgba[np.where((mask_rgba > [0, 0, 0, 0]).all(axis=2))] = [
            *currentColor,
            255,
        ]
        mask_rgba[np.where((mask_rgba == [0, 0, 0, 1]).all(axis=2))] = [0, 0, 0, 0]
        for y in range(0, shape_y):
            for x in range(0, len(mask_rgba[y])):
                b, g, r, a = mask_rgba[y][x]
                if b + g + r > 0:
                    mask_rgba[y][x][3] -= alpha_step * y
        # Merge image and mask
        canvas = Image.fromarray(np.uint8(img))
        mask_image = Image.fromarray(np.uint8(mask_rgba))
        canvas.paste(mask_image, box=(0, 0), mask=mask_image)
        return canvas

    def contours(self, img, currentColor):
        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 50, 1, cv2.THRESH_BINARY_INV)
        im2, contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
        )
        cv2.drawContours(img, contours, -1, currentColor, 1)
        return Image.fromarray(np.uint8(img))

    def pixelSortImage(self, file):
        outputFilename = "pixelsorted_{}.png".format(self.token)
        outputPath = helpers.getFilePath(
            outputFilename, path=self.pixelSortedImagePath
        )
        cmd = """
            python pixelsort/pixelsort.py {} \
            -a 180 \
            -i random \
            -r 20 \
            -c 30 \
            -o {}
        """.format(
            file, outputPath
        )
        self.log("Running pixel sort command: {}".format(cmd))
        os.system(cmd)
        return outputFilename

    def makeSlicedImage(
        self,
        images,
        sliceName="",
        canvasImgPath=None,
        canvas=None,
        minProp=0.04,
        maxProp=0.06,
        returnCanvas=True,
        maxSlicesCount=1,
        filenamePrefix="",
    ):
        if canvas is None:
            canvas = Image.open(canvasImgPath)
        width, height = canvas.size
        minSliceWidth = width * minProp
        maxSliceWidth = width * maxProp
        successCount = 0
        i = 0

        while i < len(images) and successCount < maxSlicesCount:
            image = images[i]
            i += 1
            try:
                sliceWidth = np.random.randint(minSliceWidth, maxSliceWidth)
                slicePosX = np.random.randint(0, width - sliceWidth)
                self.log("Slice {}#{}".format(sliceName, i))
                self.log("Width\t{}".format(sliceWidth))
                self.log("X\t{}\n".format(slicePosX))
                if helpers.isUrl(image):
                    image = helpers.readImageUrl(image)
                image = Image.open(image)
                image = image.resize((width, height))
                imageSlice = image.crop((slicePosX, 0, slicePosX + sliceWidth, height))
                canvas.paste(imageSlice, (slicePosX, 0))
                successCount += 1
            except Exception as e:
                self.log(e)
        if returnCanvas:
            return canvas
        else:
            fileNumber = 1
            dirName = "{0}{1:04d}".format(filenamePrefix, fileNumber)
            while os.path.isdir(
                helpers.getFilePath(dirName, path=self.finalImagePath)
            ):
                fileNumber += 1
                dirName = "{0}{1:04d}".format(filenamePrefix, fileNumber)
            filename = dirName + "/full.jpg"
            os.mkdir(helpers.getFilePath(dirName, path=self.finalImagePath))
            canvas.save(helpers.getFilePath(filename, path=self.finalImagePath))
            # Save thumbnail
            thumbnailWidth = 110
            thumbnailHeight = thumbnailWidth * (height / width)
            canvas.thumbnail((thumbnailWidth, int(thumbnailHeight)))
            filename = dirName + "/thumb.jpg"
            canvas.save(helpers.getFilePath(filename, path=self.finalImagePath))
            return dirName
