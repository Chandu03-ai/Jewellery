from pymongo import MongoClient
from constants import mongoUrl,mongoDatabase,mongoProductCollection,mongoCategoryCollection,mongoCartCollection,mongoWishlistCollection,mongoShippingCollection

client = MongoClient(mongoUrl)
db = client[mongoDatabase]
productsCollection = db[mongoProductCollection]
categoriesCollection = db[mongoCategoryCollection]
cartCollection = db[mongoCartCollection]
wishlistCollection = db[mongoWishlistCollection]
shippingCollection = db[mongoShippingCollection]



