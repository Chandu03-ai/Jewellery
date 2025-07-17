# routers/categoryRouter.py

from bson import ObjectId
from fastapi import APIRouter, Request
from Models.categoryModel import CategoryModel
from Database.categoryDb import insertCategoryIfNotExists, deleteCategoryFromDb, getCategoryFromDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse

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
            "description": payload.description,
            "image": payload.image,
            "parentCategory": payload.parentCategory,
            "sortOrder": payload.sortOrder,
            "isActive": payload.isActive,
            "metaTitle": payload.metaTitle,
            "metaDescription": payload.metaDescription,
            "productCount": payload.productCount,
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
        }

        insertCategoryIfNotExists(payload.name)  # Optional fallback
        logger.info(f"Category created successfully: {payload.name}")
        return returnResponse(2020, result=categoryData)

    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return returnResponse(2022)


@router.delete("/categories/{id}")
async def deleteCategory(id: str, request: Request):
    try:
        logger.debug(f"deleteCategorey function started for id:{id}")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to delete category")
            return returnResponse(2000)
        deleted = deleteCategoryFromDb({"id": id})
        logger.info(f"category deleted successfully for id:{id}")
        return returnResponse(2024 if deleted.deleted_count else 2025, result={"deleted": deleted.deleted_count})
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return returnResponse(2026)
