from Database.MongoData import cartCollection, wishlistCollection

def addToCartDb(item: dict):
    return cartCollection.insert_one(item)

def getCartDb(user_id: str):
    return cartCollection.find({"userId": user_id}, {"_id": 0})

def addToWishlistDb(item: dict):
    return wishlistCollection.insert_one(item)

def getWishlistDb(user_id: str):
    return wishlistCollection.find({"userId": user_id}, {"_id": 0})
