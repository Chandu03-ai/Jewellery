# routers/productRouter.py

from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Request, UploadFile, File, Query
from Models.productModel import ProductImportModel
from Database.productDb import (
    insertProductToDb,
    getAllProductsFromDb,
    deleteProductsFromDb,
    getProductBySlugFromDb,
    filterProductsFromDb,
    importHistoryCollection,
)
from Database.categoryDb import insertCategoryIfNotExists, getCategoryBySlugFromDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from Utils.imageUploader import save_image
from ReturnLog.logReturn import returnResponse

router = APIRouter(tags=["Products"])


@router.post("/importproducts")
async def import_products(request: Request, payload: List[ProductImportModel]):
    user_id = request.state.userMetadata.get("id")
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access attempt to import products")
        return returnResponse(2000)

    total, imported, failed = len(payload), 0, 0
    imported_products = []

    for product in payload:
        try:
            # Auto-create category if it doesn't exist
            insertCategoryIfNotExists(product.category)

            # Prepare product data
            product_slug = slugify(product.name)
            data = product.model_dump()
            data.update({
                "id": str(ObjectId()),
                "slug": product_slug,
                "createdBy": user_id,
                "createdAt": formatDateTime(),
                "updatedAt": formatDateTime(),
            })

            insertProductToDb(data)
            data.pop("_id", None)
            imported_products.append(data)
            imported += 1

        except Exception as e:
            failed += 1
            logger.warning(f"❌ Failed to import product [{product.name}]: {e}")

    importHistoryCollection.insert_one({
        "id": str(ObjectId()),
        "userId": user_id,
        "fileName": "frontend-payload",
        "timestamp": formatDateTime(),
        "total": total,
        "imported": imported,
        "failed": failed,
    })

    return returnResponse(2001, result=imported_products)



@router.get("/auth/products")
async def get_products():
    try:
        products = list(getAllProductsFromDb())
        return returnResponse(2005, result=products if products else [])
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return returnResponse(2004)

@router.get("/auth/products/filter")
async def filter_products(
    category: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    tags: Optional[List[str]] = Query(None),
):
    try:
        products = list(filterProductsFromDb(category, price_min, price_max, tags))

        return returnResponse(2005, result=products)
    except Exception as e:
        logger.error(f"Error filtering products: {e}")
        return returnResponse(2004)  # general failure
    
@router.get("/auth/products/{slug}")
async def get_product_by_slug(slug: str):
    try:
        product = getProductBySlugFromDb(slug)
        if not product:
            return returnResponse(2010, result=None)
        return returnResponse(2005, result=product)
    except Exception as e:
        logger.error(f"Error fetching product by slug: {e}")
        return returnResponse(2004)






@router.post("/auth/products/image-upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        image_url = save_image(file)
        return returnResponse(2011, result={"url": image_url})
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        return returnResponse(2012)


@router.delete("/deleteProducts")
async def delete_products(request: Request):
    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning("Unauthorized access attempt to delete products")
        return returnResponse(2000)
    try:
        deleted_count = deleteProductsFromDb({})
        return returnResponse(2008 if deleted_count else 2007, result={"deleted": deleted_count})
    except Exception as e:
        logger.error(f"Error deleting products: {e}")
        return returnResponse(2009)
