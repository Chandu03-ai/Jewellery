from Database.MongoData import productsCollection,importHistoryCollection

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

def deleteProductsFromDb(query: dict):
    """
    Deletes products from the database based on the provided query.
    :param query: Dictionary containing the criteria for deletion.
    :return: Number of deleted documents.
    """
    result = productsCollection.delete_many(query)
    return result.deleted_count


def getProductBySlugFromDb(slug: str):
    return productsCollection.find_one({"slug": slug}, {"_id": 0})

def filterProductsFromDb(category=None, price_min=None, price_max=None, tags=None):
    query = {}

    if category:
        query["category"] = category

    if price_min is not None or price_max is not None:
        query["price"] = {}
        if price_min is not None:
            query["price"]["$gte"] = price_min
        if price_max is not None:
            query["price"]["$lte"] = price_max

    if tags:
        query["tags"] = {"$in": tags}

    return productsCollection.find(query, {"_id": 0})

