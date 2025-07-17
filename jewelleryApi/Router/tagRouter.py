# routers/tagRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from Database.tagDb import insertTagToDb, getAllTagsFromDb, addTagsToProductInDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.tagModel import TagModel, TagUpdateModel

router = APIRouter(tags=["Tags"])


@router.post("/tags")
async def createTag(request: Request, payload: TagModel):

    try:
        logger.debug(f"creatTag function called")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to create tag")
            return returnResponse(2000)
        tagData = {
            "id": str(ObjectId()),
            "name": payload.name,
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
        }
        insertTagToDb(tagData)
        logger.info(f"tag created successfully")
        return returnResponse(2040, result=tagData)
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        return returnResponse(2042)


@router.get("/auth/tags")
async def getTags():
    try:
        logger.debug("getTags function called")
        tags = list(getAllTagsFromDb())
        if not tags:
            return returnResponse(2043, result=[])
        logger.info(f"tags fetched successfully")
        return returnResponse(2041, result=tags)
    except Exception as e:
        logger.error(f"Error fetching tags: {e}")
        return returnResponse(2042)


@router.put("/products/{productId}/tags")
async def updateProductTags(request: Request, productId: str, payload: TagUpdateModel):
    try:
        logger.debug(f"updateProducttags function called for productId: {productId}")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to update product tags")
            return returnResponse(2000)
        result = addTagsToProductInDb(productId, payload.tags)
        logger.info(f"Product tags updated successfully for productId: {productId}")
        return returnResponse(2044 if result else 2045, result={"updated": result})
    except Exception as e:
        logger.error(f"Error updating product tags: {e}")
        return returnResponse(2046)
