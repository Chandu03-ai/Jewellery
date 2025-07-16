# routers/reviewRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Optional
from Database.reviewDb import (
    insertReviewToDb,
    getReviewsByProductIdFromDb,
    updateProductRatingInDb
)
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.reviewModel import ReviewModel
router = APIRouter(tags=["Reviews"])



@router.post("/products/{product_id}/reviews")
async def add_review(request: Request, product_id: str, payload: ReviewModel):
    try:
        review_data = {
            "id": str(ObjectId()),
            "productId": product_id,
            "userId": payload.userId,
            "rating": payload.rating,
            "comment": payload.comment,
            "createdAt": formatDateTime(),
        }
        insertReviewToDb(review_data)
        updateProductRatingInDb(product_id)
        return returnResponse(2050, result=review_data)
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        return returnResponse(2052)

@router.get("/auth/products/{product_id}/reviews")
async def get_reviews(product_id: str):
    try:
        reviews = list(getReviewsByProductIdFromDb(product_id))
        if not reviews:
            return returnResponse(2053, result=[])
        return returnResponse(2051, result=reviews)
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        return returnResponse(2052)
