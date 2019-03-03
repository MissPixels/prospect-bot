import os
import logging
import configparser
import string
import random
import urllib
from io import BytesIO


def log(message):
    writeLogs = int(os.getenv("WRITE_LOGS", False))
    logFile = os.getenv("LOG_FILE", None)
    logging.basicConfig(filename=logFile, level=logging.DEBUG)
    if writeLogs >= 1:
        print(message)
    if writeLogs == 2 and logFile is not None:
        logging.debug(message)


def getConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config


def getRandomToken(N=5):
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(N)
    )


def getFilePath(filename, path="", withRoot=True):
    root = getConfig()["Files"]["Root"]
    path = "{}{}".format(path, filename)
    if withRoot:
        path = "{}/{}".format(root, path)
    return path


def isUrl(string):
    return urllib.parse.urlparse(string).scheme != ""


def readImageUrl(url):
    return BytesIO(urllib.request.urlopen(url).read())


def nl2br(string):
    return string.replace("\n", "<br>")


def isAuthorizedRequest(request):
    token = os.getenv("TOKEN", None)
    if token is None:
        return True
    return request.headers.get("Authorization") == token
