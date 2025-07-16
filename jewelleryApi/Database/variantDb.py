from Database.MongoData import variantsCollection

def insertVariantToDb(data: dict):
    return variantsCollection.insert_one(data)

def getAllVariantsFromDb():
    return variantsCollection.find({}, {"_id": 0})
