import os
import twitter


class Tweeter(object):
    def __init__(self):
        super(Tweeter, self).__init__()
        self.api = twitter.Api(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY", None),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET", None),
            access_token_key=os.getenv("TWITTER_ACCESS_TOKEN_KEY", None),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", None),
        )

    def tweet(self, poem, image, additionalText=None):
        text = poem + "\n#Pröspect"
        if additionalText is not None:
            text += " " + additionalText
        self.api.PostUpdate(text, media=image)
