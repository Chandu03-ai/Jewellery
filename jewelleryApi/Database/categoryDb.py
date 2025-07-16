# Database/categoryDb.py

from bson import ObjectId
from Database.MongoData import categoriesCollection
from Utils.slugify import slugify
from yensiDatetime.yensiDatetime import formatDateTime

def insertCategoryIfNotExists(name: str):
    slug = slugify(name)
    existing = getCategoryFromDb({"slug": slug})
    if not existing:
        categoriesCollection.insert_one({
            "id": str(ObjectId()),
            "name": name,
            "slug": slug,
            "description": "",
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
        })

def getCategoriesFromDb(query: dict = {}, projection: dict = {"_id": 0}):
    return categoriesCollection.find(query, projection)

def getCategoryFromDb(query: dict):
    return categoriesCollection.find_one(query, {"_id": 0})

def deleteCategoryFromDb(query: dict):
    return categoriesCollection.delete_one(query)
