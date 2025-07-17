from bson import ObjectId
from fastapi import Request
from yensiAuthentication import logger
from yensiDatetime.yensiDatetime import formatDateTime
from Utils.slugify import slugify
from Models.categoryModel import CategoryModel
from Database.categoryDb import getCategoryFromDb, insertCategoryIfNotExists
from Database.tagDb import getTagFromDb, insertTagToDb
from Models.tagModel import TagModel


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


def buildTagDocument(tags: list):
    if not tags or not isinstance(tags, list):
        return

    for tag in tags:
        if not isinstance(tag, dict) or "name" not in tag:
            continue  # skip invalid entries

        slug = slugify(tag["name"])
        existing = getTagFromDb({"slug": slug})

        if not existing:
            now = formatDateTime()
            tagData = TagModel(
                name=tag["name"], slug=slug, color=tag.get("color", "#000000"), isActive=tag.get("isActive", True), sortOrder=tag.get("sortOrder", 0), productCount=tag.get("productCount", 0)
            ).model_dump()

            tagData["createdAt"] = now
            tagData["updatedAt"] = now
            tagData["id"] = str(ObjectId())
            insertTagToDb(tagData)
