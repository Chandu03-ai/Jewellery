from bson import ObjectId
from fastapi import APIRouter, Request
from Database.variantDb import insertVariantToDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.variantModel import VariantModel

router = APIRouter(prefix="/admin", tags=["Admin-Variants"])


@router.post("/variants")
async def createVariant(request: Request, payload: VariantModel):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access to create variant")
        return returnResponse(2000)

    try:
        now = formatDateTime()
        variantData = payload.model_dump()
        variantData.update(
            {
                "id": str(ObjectId()),
                "createdAt": now,
                "updatedAt": now,
            }
        )
        insertVariantToDb(variantData)
        logger.info(f"Variant created: {variantData}")
        return returnResponse(2030, result=variantData)
    except Exception as e:
        logger.error(f"Error creating variant: {e}")
        return returnResponse(2032)
