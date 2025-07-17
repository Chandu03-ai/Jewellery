# routers/productRouter.py
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Request
from Models.productModel import ProductImportModel
from Database.productDb import insertProductToDb,  getProductFromDb, updateProductInDb, deleteProductFromDb, deleteProductsFromDb, insertImportHistoryToDb
from Database.categoryDb import insertCategoryIfNotExists
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse

router = APIRouter(prefix="/admin",tags=["Products"])


@router.post("/product/importProducts")
async def importProducts(request: Request, payload: List[ProductImportModel]):
    userId = request.state.userMetadata.get("id")

    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning(f"Unauthorized access attempt by user [{userId}] to import products.")
        return returnResponse(2000)
    logger.info(f"Starting product import by user [{userId}]. Total products received: {len(payload)}")
    total, imported, updated, failed = len(payload), 0, 0, 0
    processedProducts = []
    for product in payload:
        try:
            logger.debug(f"Processing product: {product.name}")
            insertCategoryIfNotExists(product.category)

            slug = slugify(product.name)
            productDict = product.model_dump()
            productDict.update({"slug": slug, "updatedAt": formatDateTime()})
            existing = getProductFromDb({"slug": slug})

            if existing:
                productDict["id"] = existing["id"]
                productDict["noOfProducts"] = existing.get("noOfProducts", 0) + product.noOfProducts
                updateProductInDb({"slug": slug}, productDict)
                updated += 1
                logger.info(f"Updated existing product quantity: {product.name} (slug: {slug})")
            else:
                productDict.update({"id": str(ObjectId()), "createdBy": userId, "createdAt": formatDateTime()})
                insertProductToDb(productDict)
                imported += 1
                logger.info(f"Inserted new product: {product.name} (slug: {slug})")

            productDict.pop("_id", None)
            processedProducts.append(productDict)

        except Exception as e:
            failed += 1
            logger.error(f"Error importing/updating product [{product.name}]: {str(e)}")

    insertImportHistoryToDb(
        {
            "id": str(ObjectId()),
            "userId": userId,
            "fileName": "frontend-payload",
            "timestamp": formatDateTime(),
            "total": total,
            "imported": imported,
            "updated": updated,
            "failed": failed,
        }
    )

    logger.info(f"Product import completed by user [{userId}]. Summary - Total: {total}, Inserted: {imported}, Updated: {updated}, Failed: {failed}")
    return returnResponse(2001, result=processedProducts)


@router.put("/product/id/{productId}")
async def updateProductByIdEndpoint(productId: str, request: Request, payload: ProductImportModel):
    try:
        logger.debug(f"updateProductByIdEndpoint function started for productId:{productId}")
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized update attempt by user [{userId}] on product ID: {productId}")
            return returnResponse(2000)
        logger.info(f"User [{userId}] is attempting to update product with ID: {productId}")

        existing = getProductFromDb({"id": productId})
        if not existing:
            logger.warning(f"No product found with ID: {productId}")
            return returnResponse(2016, message="Product not found for update.")

        updatePayload = payload.model_dump()
        updatePayload.update(
            {"id": productId, "slug": slugify(payload.name), "updatedAt": formatDateTime(), "createdBy": existing.get("createdBy", userId), "createdAt": existing.get("createdAt", formatDateTime())}
        )

        if updatePayload.get("noOfProducts", 0) <= 0:
            updatePayload["inStock"] = False

        updateProductInDb({"id": productId}, updatePayload)

        logger.info(f"Product [ID: {productId}] updated by user [{userId}]")
        updatePayload.pop("_id", None)
        return returnResponse(2018, result=updatePayload)

    except Exception as e:
        logger.error(f"Failed to update product [ID: {productId}] by user [{userId}]: {str(e)}")
        return returnResponse(2019, message="Error occurred while updating product.")


@router.delete("/product/deleteProducts")
async def deleteProducts(request: Request):

    try:
        logger.debug(f"deleteProducts function started")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access attempt to delete products")
            return returnResponse(2000)
        deleted_count = deleteProductsFromDb({})
        logger.info(f"deleted products successfully")
        return returnResponse(2008 if deleted_count else 2007, result={"deleted": deleted_count})
    except Exception as e:
        logger.error(f"Error deleting products: {e}")
        return returnResponse(2009)


@router.delete("/product/{productId}")
async def deleteProductById(request: Request, productId: str):
    try:
        logger.debug(f"deleteProductById function started for productId: {productId}")
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized access attempt by user [{userId}] to delete product [{productId}]")
            return returnResponse(2000)
        result = deleteProductFromDb({"id": productId})
        if result.deleted_count:
            logger.info(f"Product [{productId}] deleted by user [{userId}]")
            return returnResponse(2015, result={"deleted": 1})
        else:
            logger.info(f"Product [{productId}] not found for deletion by user [{userId}]")
            return returnResponse(2016, result={"deleted": 0})
    except Exception as e:
        logger.error(f"Error deleting product [{productId}] by user [{userId}]: {str(e)}")
        return returnResponse(2017)


@router.put("/product/{productId}/stock")
async def updateStock(request: Request, productId: str, payload: dict = Body(...)):
    try:
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized stock update by user [{userId}]")
            return returnResponse(2000)

        quantity = payload.get("quantity", 0)
        stockStatus = quantity > 0

        updateProductInDb({"id": productId}, {"noOfProducts": quantity, "inStock": stockStatus})
        logger.info(f"Stock updated for product [{productId}] to {quantity} by user [{userId}]")
        return returnResponse(2093)
    except Exception as e:
        logger.error(f"Error updating stock for product [{productId}]: {e}")
        return returnResponse(2094)





