from pymongo import MongoClient
from constants import mongoUrl,mongoDatabase,mongoProductCollection,mongoImportHistoryCollection

client = MongoClient(mongoUrl)
db = client[mongoDatabase]
productsCollection = db[mongoProductCollection]
importHistoryCollection = db[mongoImportHistoryCollection]

