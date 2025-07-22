from Database.MongoData import cartCollection, wishlistCollection


def addToCartDb(item: dict):
    return cartCollection.insert_one(item)

def addBulkToCartDb(item: dict):
    return cartCollection.insert_many(item)


def updateCartDb(query: dict, item: dict):
    return cartCollection.update_one(query, {"$set": item})


def updateCartManyDb(query: dict, item: dict):
    return cartCollection.update_many(query, {"$set": item})


def updateQuantityCartDb(query: dict, updateOperation: dict):
    return cartCollection.update_one(query, updateOperation)


def getSingleCartDb(query: dict):
    return cartCollection.find_one(query, {"_id": 0})


def getCartDb(query: dict):
    return cartCollection.find(query, {"_id": 0})


