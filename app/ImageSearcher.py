from io import FileIO
import urllib
from google.cloud import vision
from google.cloud.vision import types
from mimetypes import guess_type, guess_extension

from app.Base import Base


class ImageSearcher(Base):
    def __init__(self):
        super(ImageSearcher, self).__init__()
        self.client = vision.ImageAnnotatorClient()
        self.log("\n* ImageSearcher initialized")

    def searchWithUrl(self, url):
        self.log("Searching images similar to URL {}".format(url))
        content = urllib.request.urlopen(url).read()
        return self.searchVisuallySimilarImages(content)

    def searchWithLocalFile(self, file):
        self.log("Searching images similar to file {}".format(file))
        fileBuffer = FileIO(file)
        content = fileBuffer.read()
        return self.searchVisuallySimilarImages(content)

    def searchVisuallySimilarImages(self, content):
        similar_images = []
        try:
            image = types.Image(content=content)
            response = self.client.web_detection(image=image)
            for similar_image in response.web_detection.visually_similar_images:
                [mimeType, encoding] = guess_type(similar_image.url)
                if mimeType is not None:
                    extension = guess_extension(type=mimeType)
                    similar_images.append(
                        {
                            "title": "{0}{1}".format(len(similar_images), extension),
                            "link": similar_image.url,
                        }
                    )
        except Exception as e:
            self.log(e)
        return similar_images
