# routers/tagRouter.py

from fastapi import APIRouter
from Database.tagDb import getAllTagsFromDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse

router = APIRouter(prefix="/public", tags=["Tags"])


@router.get("/tags")
async def getTags():
    try:
        logger.debug("getTags function called")
        tags = list(getAllTagsFromDb())
        if not tags:
            logger.info("No tags found")
            return returnResponse(2043, result=[])
        logger.info(f"tags fetched successfully")
        return returnResponse(2041, result=tags)
    except Exception as e:
        logger.error(f"Error fetching tags: {e}")
        return returnResponse(2042)
