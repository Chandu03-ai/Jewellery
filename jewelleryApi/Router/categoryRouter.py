# routers/categoryRouter.py

from bson import ObjectId
from fastapi import APIRouter, Request
from Models.categoryModel import CategoryModel
from Database.categoryDb import (
    insertCategoryIfNotExists,
    getAllCategoriesFromDb,
    deleteCategoryByIdFromDb
)
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse

router = APIRouter(tags=["Categories"])

@router.post("/categories")
async def create_category(request: Request, payload: CategoryModel):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access to create category")
        return returnResponse(2000)

    try:
        # Prevent duplicate category creation
        insertCategoryIfNotExists(payload.name)

        # Return consistent result payload
        category_data = {
            "id": str(ObjectId()),
            "name": payload.name,
            "slug": slugify(payload.name),
            "description": payload.description,
            "createdAt": formatDateTime(),
            "updatedAt": formatDateTime(),
        }

        return returnResponse(2020, result=category_data)
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return returnResponse(2022)

@router.get("/auth/categories")
async def get_categories():
    try:
        categories = list(getAllCategoriesFromDb())
        return returnResponse(2021, result=categories or [])
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return returnResponse(2022)

@router.delete("/categories/{id}")
async def delete_category(id: str, request: Request):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access to delete category")
        return returnResponse(2000)

    try:
        deleted = deleteCategoryByIdFromDb(id)
        return returnResponse(2024 if deleted else 2025, result={"deleted": deleted})
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return returnResponse(2026)
