from app.Base import Base
from app.ImagePicker.McCordPicker import McCordPicker


class ImagePicker(Base):
    def __init__(self):
        super(ImagePicker, self).__init__()
        self.log("\n* ImagePicker initialized")

    def pickImage(self, source=None, unique=lambda image: True):
        if source is None:
            source = "mccord"
        picker = None
        image = None
        if source == "mccord":
            picker = McCordPicker()
        if picker is not None:
            while image is None or not unique(image):
                image = picker.pickImage()
        return image

