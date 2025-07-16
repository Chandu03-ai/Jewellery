# routers/variantRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Literal
from Database.variantDb import insertVariantToDb, getAllVariantsFromDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse

router = APIRouter(tags=["Variants"])

class VariantModel(BaseModel):
    type: Literal["size", "metal", "stone"]
    value: str


@router.post("/variants")
async def create_variant(request: Request, payload: VariantModel):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access to create variant")
        return returnResponse(2000)
    try:
        variant_data = {
            "id": str(ObjectId()),
            "type": payload.type,
            "value": payload.value,
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
        }
        insertVariantToDb(variant_data)
        return returnResponse(2030, result=variant_data)
    except Exception as e:
        logger.error(f"Error creating variant: {e}")
        return returnResponse(2032)


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
