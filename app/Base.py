from datetime import datetime

from app.utils import helpers


class Base:
    def __init__(self):
        super(Base, self).__init__()
        self.log = helpers.log

    def getConfig(self):
        return helpers.getConfig()

    def formatDuration(self, duration):
        return duration

    def timestampToDate(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
