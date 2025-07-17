# Database/categoryDb.py

from Database.MongoData import categoriesCollection


def insertCategoryIfNotExists(data: dict):
    return categoriesCollection.insert_one(data)


def getCategoriesFromDb(query: dict = {}, projection: dict = {"_id": 0}):
    return categoriesCollection.find(query, projection)


def getCategoryFromDb(query: dict):
    return categoriesCollection.find_one(query, {"_id": 0})


def deleteCategoryFromDb(query: dict):
    return categoriesCollection.delete_one(query)
