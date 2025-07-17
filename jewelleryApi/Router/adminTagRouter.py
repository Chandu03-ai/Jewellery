# routers/adminTagRouter.py

from bson import ObjectId
from fastapi import APIRouter, Request
from Database.tagDb import insertTagToDb, addTagsToProductInDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.tagModel import TagModel, TagUpdateModel
from Utils.slugify import slugify

router = APIRouter(prefix="/admin", tags=["Admin-Tags"])


@router.post("/tags")
async def createTag(request: Request, payload: TagModel):
    try:
        logger.debug("createTag function called")

        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to create tag")
            return returnResponse(2000)

        slug = slugify(payload.name)
        tagData = payload.model_copy(update={"id": str(ObjectId()), "slug": slug, "createdAt": formatDateTime(), "updatedAt": formatDateTime()}).model_dump()

        insertTagToDb(tagData)
        tagData.pop("_id", None)

        logger.info(f"Tag [{payload.name}] created successfully")
        return returnResponse(2040, result=tagData)

    except Exception as e:
        logger.error(f"Error creating tag: {e}")
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
