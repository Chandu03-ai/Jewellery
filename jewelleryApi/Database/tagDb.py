from Database.MongoData import tagsCollection, productsCollection

def insertTagToDb(data: dict):
    return tagsCollection.insert_one(data)

def getAllTagsFromDb():
    return tagsCollection.find({}, {"_id": 0})

def addTagsToProductInDb(product_id: str, tags: list[str]):
    result = productsCollection.update_one(
        {"id": product_id},
        {"$set": {"tags": tags}}
    )
    return result.modified_count > 0
