# routers/categoryRouter.py

from bson import ObjectId
from fastapi import APIRouter, Request
from Models.categoryModel import CategoryModel, UpdateCategoryModel
from Database.categoryDb import insertCategoryIfNotExists, getCategoryFromDb, updateCategoryInDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse
from Database.productDb import getProductsFromDb, updateProductInDb

router = APIRouter(prefix="/admin", tags=["Admin-Categories"])


@router.post("/categories")
async def createCategory(request: Request, payload: CategoryModel):
    try:
        logger.info("createCategory function started")

        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to create category")
            return returnResponse(2000)

        slug = slugify(payload.slug or payload.name)

        existing = getCategoryFromDb({"slug": slug})
        if existing:
            logger.info(f"Category already exists: {payload.name}")
            return returnResponse(2023, result=existing)

        categoryData = {
            "id": str(ObjectId()),
            "name": payload.name,
            "slug": slug,
            "image": payload.image,
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
            "isDeleted": False,
        }

        insertCategoryIfNotExists(categoryData)
        categoryData.pop("_id", None)
        logger.info(f"Category created successfully: {payload.name}")
        return returnResponse(2020, result=categoryData)

    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return returnResponse(2022)


@router.delete("/categories/{id}")
async def deleteCategory(request: Request, id: str):
    try:
        logger.debug(f"deleteCategorey function started for id:{id}")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to delete category")
            return returnResponse(2000)
        category = getCategoryFromDb({"id": id, "isDeleted": False})
        if not category:
            logger.warning(f"category not found for id:{id}")
            return returnResponse(2105)
        categoryName = category.get("slug")
        productData = list(getProductsFromDb({"category": categoryName, "isDeleted": False}))
        if productData:
            for category in productData:
                logger.info(f"category deleteing in productd for Name:{categoryName}")
                updateProductInDb({"category": categoryName}, {"isDeleted": True})
                logger.info(f"category deleted successfully in Products :{categoryName}")
        updateCategoryInDb({"id": id}, {"isDeleted": True})
        logger.info(f"category deleted successfully for id:{id}")
        return returnResponse(2024)
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return returnResponse(2026)


@router.put("/categories/{categoryId}")
async def updateCategory(request: Request, categoryId: str, payload: UpdateCategoryModel):
    try:
        logger.info(f"updateCategory called for ID: {categoryId}")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to update category")
            return returnResponse(2000)
        existing = getCategoryFromDb({"id": categoryId, "isDeleted": False})
        if not existing:
            logger.info(f"No category found with ID: {categoryId}")
            return returnResponse(2113)
        updateData = {}
        if payload.name:
            updateData["name"] = payload.name
        if payload.slug or payload.name:
            updateData["slug"] = slugify(payload.slug or payload.name)
        if payload.image is not None:
            updateData["image"] = payload.image
        updateData["updatedAt"] = formatDateTime()
        updateCategoryInDb({"id": categoryId}, updateData)
        updated = getCategoryFromDb({"id": categoryId})
        updated.pop("_id", None)
        logger.info(f"Category updated successfully: {categoryId}")
        return returnResponse(2114, result=updated)
    except Exception as e:
        logger.error(f"Error updating category [{categoryId}]: {e}")
        return returnResponse(2115)
