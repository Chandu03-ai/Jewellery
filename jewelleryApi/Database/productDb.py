from MongoData import productsCollection,importHistoryCollection

# Product Collection Methods

def insertProductToDb(product: dict):
    return productsCollection.insert_one(product)


def getAllProductsFromDb(query: dict = {}, projection: dict = {"_id": 0}):
    return productsCollection.find(query, projection)


def getProductByIdFromDb(productId: str):
    return productsCollection.find_one({"_id": productId})


def getProductsByCategoryFromDb(category: str):
    return productsCollection.find({"category": category})


def getFeaturedProductsFromDb():
    return productsCollection.find({"featured": True})


def searchProductsInDb(query: str):
    return productsCollection.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    })


# Import History Collection Methods

def insertImportHistoryToDb(historyData: dict):
    return importHistoryCollection.insert_one(historyData)


def getImportHistoryFromDb():
    return importHistoryCollection.find({}, {"_id": 0}).sort("timestamp", -1)
