# routers/reviewRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from Database.reviewDb import insertReviewToDb, getReviewsByProductIdFromDb, updateProductRatingInDb
from yensiDatetime.yensiDatetime import formatDateTime
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.reviewModel import ReviewModel

router = APIRouter(tags=["Reviews"])


@router.post("/products/{productId}/reviews")
async def addReview(request: Request, productId: str, payload: ReviewModel):
    try:
        logger.debug(f"addreview function started for productId:{productId}")
        reviewData = {
            "id": str(ObjectId()),
            "productId": productId,
            "userId": payload.userId,
            "rating": payload.rating,
            "comment": payload.comment,
            "createdAt": formatDateTime(),
        }
        insertReviewToDb(reviewData)
        updateProductRatingInDb(productId)
        logger.info(f"review added successfully for product:{productId}")
        return returnResponse(2050, result=reviewData)
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        return returnResponse(2052)


@router.get("/auth/products/{productId}/reviews")
async def getReviews(productId: str):
    try:
        logger.debug(f"getReviews function started for productId:{productId}")
        reviews = list(getReviewsByProductIdFromDb(productId))
        if not reviews:
            return returnResponse(2053, result=[])
        logger.info(f"reviews fetched successfully for product:{productId}")
        return returnResponse(2051, result=reviews)
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        return returnResponse(2052)
