from Database.MongoData import reviewsCollection, productsCollection
from pymongo import DESCENDING

def insertReviewToDb(data: dict):
    return reviewsCollection.insert_one(data)

def getReviewsByProductIdFromDb(product_id: str):
    return reviewsCollection.find({"productId": product_id}).sort("createdAt", DESCENDING)

def updateProductRatingInDb(product_id: str):
    reviews = list(reviewsCollection.find({"productId": product_id}))
    if not reviews:
        return
    avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 2)
    total_reviews = len(reviews)
    productsCollection.update_one(
        {"id": product_id},
        {"$set": {"rating": avg_rating, "reviews": total_reviews}}
    )
