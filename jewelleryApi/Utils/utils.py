from bson import ObjectId
from fastapi import Request
from yensiAuthentication import logger
from yensiDatetime.yensiDatetime import formatDateTime
from Utils.slugify import slugify
from Models.categoryModel import CategoryModel
from Database.categoryDb import getCategoryFromDb, insertCategoryIfNotExists




def hasRequiredRole(request: Request, requiredRoles: list):
    userMetadata = request.state.userMetadata
    userRole = userMetadata.get("role")

    if not userRole in requiredRoles:
        logger.warning("Unauthorized access attempt by user with roles: %s", userRole)
        return False
    return True


def buildCategoryDocument(name: str):
    slug = slugify(name)
    existing = getCategoryFromDb({"slug": slug})
    if not existing:
        now = formatDateTime()
        data = CategoryModel(
            name=name,
            slug=slug,
            description="",
        ).model_dump()
        data["createdAt"] = now
        data["updatedAt"] = now
        data["id"] = str(ObjectId())
        insertCategoryIfNotExists(data)

