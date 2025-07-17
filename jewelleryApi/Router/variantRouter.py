# routers/variantRouter.py
from fastapi import APIRouter
from Database.variantDb import getAllVariantsFromDb

from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse

router = APIRouter(prefix="/public", tags=["Variants"])


@router.get("/auth/variants")
async def get_variants():
    try:
        variants = list(getAllVariantsFromDb())
        if not variants:
            return returnResponse(2033, result=[])
        return returnResponse(2031, result=variants)
    except Exception as e:
        logger.error(f"Error fetching variants: {e}")
        return returnResponse(2032)
