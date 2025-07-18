from Database.MongoData import reviewsCollection, productsCollection
from pymongo import DESCENDING

def insertReviewToDb(data: dict):
    return reviewsCollection.insert_one(data)

def getReviewsByProductIdFromDb(productId: str):
    return reviewsCollection.find({"productId": productId}).sort("createdAt", DESCENDING)

def updateProductRatingInDb(productId: str):
    reviews = list(reviewsCollection.find({"productId": productId}))
    if not reviews:
        return
    avgRating = round(sum(r["rating"] for r in reviews) / len(reviews), 2)
    totalReviews = len(reviews)
    productsCollection.update_one(
        {"id": productId},
        {"$set": {"rating": avgRating, "reviews": totalReviews}}
    )
