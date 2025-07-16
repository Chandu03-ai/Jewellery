from Database.MongoData import productsCollection, importHistoryCollection

# ───── Product Collection Methods ───── #

def insertProductToDb(product: dict):
    return productsCollection.insert_one(product)

def getProductsFromDb(query: dict = {}, projection: dict = {"_id": 0}):
    return productsCollection.find(query, projection)

def getProductFromDb(query: dict, projection: dict = {"_id": 0}):
    return productsCollection.find_one(query, projection)

def updateProductInDb(query: dict, updateData: dict):
    return productsCollection.update_one(query, {"$set": updateData})

def deleteProductFromDb(query: dict):
    return productsCollection.delete_one(query)

def deleteProductsFromDb(query: dict):
    return productsCollection.delete_many(query).deleted_count

# ───── Import History Methods ───── #

def insertImportHistoryToDb(data: dict):
    return importHistoryCollection.insert_one(data)

def getImportHistoryFromDb():
    return importHistoryCollection.find({}, {"_id": 0}).sort("timestamp", -1)
