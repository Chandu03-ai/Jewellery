# routers/tagRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from pydantic import BaseModel
from Database.tagDb import insertTagToDb, getAllTagsFromDb, addTagsToProductInDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.tagModel import TagModel, TagUpdateModel
router = APIRouter(tags=["Tags"])



@router.post("/tags")
async def create_tag(request: Request, payload: TagModel):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access to create tag")
        return returnResponse(2000)
    try:
        tag_data = {
            "id": str(ObjectId()),
            "name": payload.name,
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
        }
        insertTagToDb(tag_data)
        return returnResponse(2040, result=tag_data)
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        return returnResponse(2042)


@router.get("/auth/tags")
async def get_tags():
    try:
        tags = list(getAllTagsFromDb())
        if not tags:
            return returnResponse(2043, result=[])
        return returnResponse(2041, result=tags)
    except Exception as e:
        logger.error(f"Error fetching tags: {e}")
        return returnResponse(2042)


@router.put("/products/{product_id}/tags")
async def update_product_tags(request: Request, product_id: str, payload: TagUpdateModel):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access to update product tags")
        return returnResponse(2000)
    try:
        result = addTagsToProductInDb(product_id, payload.tags)
        return returnResponse(2044 if result else 2045, result={"updated": result})
    except Exception as e:
        logger.error(f"Error updating product tags: {e}")
        return returnResponse(2046)