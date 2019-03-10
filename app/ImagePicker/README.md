
# Image pickers

Place images picking modules here. You should define at least an `ImagePicker` class with a `pickImage()` method which should return a dictionary in the following format:

```py
{
    "url": "",          # string: The picked image's URL
    "sourceId": "",     # string: The source's identifier
    "source": "",       # string: The source's title
    "description": "",  # string: Some text to describe the image
    "twitterText": "",  # string: Some text to be sent to be posted on Twitter along with the image
}
```

Here's a sample `ImagePicker.py`:


```py
# ImagePicker.py

from app.Base import Base


class ImagePicker(Base):
    def __init__(self):
        super(ImagePicker, self).__init__()

    def pickImage(self, source="", unique=lambda image: True):
        # Your image picking logic goes here
        # Use the source parameter to switch between multiple pickers if needed
        # The unique lambda function should let you check wether or not picked images are
        # already persisted in the DB
        return {
            "url": "",          # string: The picked image's URL
            "sourceId": "",     # string: The source's identifier
            "source": "",       # string: The source's title
            "description": "",  # string: Some text to describe the image
            "twitterText": "",  # string: Some text to be sent to be posted on Twitter along with the image
        }

```