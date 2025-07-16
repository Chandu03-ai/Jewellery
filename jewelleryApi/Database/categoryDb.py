# Database/categoryDb.py

from bson import ObjectId
from Database.MongoData import categoriesCollection
from Utils.slugify import slugify
from yensiDatetime.yensiDatetime import formatDateTime


def insertCategoryIfNotExists(name: str):
    slug = slugify(name)
    exists = categoriesCollection.find_one({"slug": slug})
    if not exists:
        categoriesCollection.insert_one(
            {
                "id": str(ObjectId()),
                "name": name,
                "slug": slug,
                "description": "",
                "createdAt": formatDateTime(),
                "updatedAt": formatDateTime(),
            }
        )


def getAllCategoriesFromDb():
    return categoriesCollection.find({}, {"_id": 0})


def deleteCategoryByIdFromDb(category_id: str):
    result = categoriesCollection.delete_one({"id": category_id})
    return result.deleted_count


def getCategoryBySlugFromDb(slug: str):
    return categoriesCollection.find_one({"slug": slug})
