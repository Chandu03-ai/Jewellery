from Database.MongoData import productsCollection

# ───── Product Collection Methods ───── #

def insertProductToDb(product: dict):
    return productsCollection.insert_one(product)

def getProductsFromDb(query: dict = {}, projection: dict = {"_id": 0}):
    return productsCollection.find(query, projection)

def getProductFromDb(query: dict, projection: dict = {"_id": 0}):
    return productsCollection.find_one(query, projection)

def updateProductInDb(query: dict, updateData: dict):
    return productsCollection.update_one(query, {"$set": updateData})

def updateManyProductsInDb(query: dict, updateData: dict):
    return productsCollection.update_many(query, {"$set": updateData})

def deleteProductFromDb(query: dict):
    return productsCollection.delete_one(query)

def deleteProductsFromDb(query: dict):
    return productsCollection.delete_many(query).deleted_count


