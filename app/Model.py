import os
from pymongo import MongoClient
from bson.objectid import ObjectId

from app.Base import Base


class Model(Base):
    def __init__(self):
        super(Model, self).__init__()
        self.client = MongoClient(
            os.getenv("DB_HOST", "localhost"), int(os.getenv("DB_PORT", 27017))
        )
        self.db = self.client[os.getenv("DB_NAME", "prospect")]
        self.collection = self.db.entries
        self.log("\n* Model intialized")

    def insert(self, data):
        return self.collection.insert_one(data).inserted_id

    def getAll(self):
        return self.collection.find({"active": True})

    def getLast(self):
        return (
            self.collection.find({"active": True}).sort([("$natural", -1)]).limit(1)[0]
        )

    def getOne(self, id):
        id = ObjectId(id)
        return self.collection.find_one({"_id": id})

    def getOneBySlug(self, slug):
        return self.collection.find_one({"slug": slug})

    def getPage(self, page, size, fetchNext=False):
        p = 1
        s = 10
        if page is not None and page.isdigit():
            page = int(page)
            if page > 0:
                p = page
        if size is not None and size.isdigit():
            size = int(size)
            if size > 0:
                s = size
        cursorStart = (p - 1) * s
        limit = s
        if fetchNext:
            limit += 1
        return (
            self.collection.find({"active": True})
            .sort([("$natural", -1)])
            .skip(cursorStart)
            .limit(limit)
        )

    def getCount(self, query={}):
        return self.collection.count_documents(query)
