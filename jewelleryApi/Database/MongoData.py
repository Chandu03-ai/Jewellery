from pymongo import MongoClient
from constants import mongoUrl,mongoDatabase,mongoProductCollection,mongoTagsCollection,mongoReviewsCollection,mongoImportHistoryCollection,mongoCategoryCollection,mongoVariantsCollection,mongoCartCollection,mongoWishlistCollection

client = MongoClient(mongoUrl)
db = client[mongoDatabase]
productsCollection = db[mongoProductCollection]
importHistoryCollection = db[mongoImportHistoryCollection]
categoriesCollection = db[mongoCategoryCollection]
variantsCollection = db[mongoVariantsCollection]
cartCollection = db[mongoCartCollection]
wishlistCollection = db[mongoWishlistCollection]
reviewsCollection = db[mongoReviewsCollection]
tagsCollection = db[mongoTagsCollection]


