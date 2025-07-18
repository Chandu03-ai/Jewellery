# routers/categoryRouter.py

from fastapi import APIRouter
from Database.categoryDb import getCategoriesFromDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse

router = APIRouter(prefix="/public", tags=["Categories"])


@router.get("/categories")
async def getCategories():
    try:
        logger.debug(f"fetching all categories")
        categories = list(getCategoriesFromDb({"isDeleted":False,"isActive":True}))
        logger.info(f"fetched all categories successfully")
        return returnResponse(2021, result=categories or [])
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return returnResponse(2022)
