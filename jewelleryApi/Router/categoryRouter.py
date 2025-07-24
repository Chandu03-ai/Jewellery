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
        categories = list(getCategoriesFromDb({"isDeleted": False}))
        logger.info(f"fetched all categories successfully")
        return returnResponse(2021, result=categories or [])
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return returnResponse(2022)


@router.get("/category/{parentId}")
async def getCategoriesByParentId(parentId: str):
    try:
        logger.debug(f"Fetching categories with parentId: {parentId}")
        categories = list(getCategoriesFromDb({"parentId": parentId, "isDeleted": False}))
        logger.info(f"Fetched categories for parentId: {parentId}")
        return returnResponse(2129, result=categories or [])
    except Exception as e:
        logger.error(f"Error fetching categories by parentId [{parentId}]: {e}")
        return returnResponse(2130)
