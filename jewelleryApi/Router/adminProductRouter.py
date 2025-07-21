# routers/adminProductRouter.py
from bson import ObjectId
from fastapi import APIRouter, Body, Request
from Models.productModel import ProductImportModel
from Database.productDb import getProductsFromDb, updateManyProductsInDb, insertProductToDb, getProductFromDb, updateProductInDb
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse
from Razor_pay.Database.ordersDb import getAllOrders

router = APIRouter(prefix="/admin", tags=["Admin-Products"])


@router.post("/product/create")
async def createProduct(request: Request, payload: ProductImportModel):
    try:
        userId = request.state.userMetadata.get("id")

        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized access attempt by user [{userId}] to create product.")
            return returnResponse(2000)

        logger.info(f"Product creation started by user [{userId}] for product: {payload.name}")

        slug = slugify(payload.slug or payload.name)
        productDict = payload.model_dump()
        productDict.update({"slug": slug, "updatedAt": formatDateTime()})

        existing = getProductFromDb({"slug": slug, "isDeleted": False})

        if existing:
            productDict["id"] = existing["id"]
            updateProductInDb({"slug": slug, "isDeleted": False}, productDict)
            logger.info(f"Updated existing product: {payload.name} (slug: {slug})")
        else:
            productDict.update({"id": str(ObjectId()), "createdBy": userId, "createdAt": formatDateTime(), "isDeleted": False})
            insertProductToDb(productDict)
            logger.info(f"Inserted new product: {payload.name} (slug: {slug})")

        productDict.pop("_id", None)
        logger.info(f"Product creation completed by user [{userId}]")
        return returnResponse(2001, result=productDict)

    except Exception as e:
        logger.error(f"[IMPORT_ERROR] Error creating product [{payload.name}]: {str(e)}")
        return returnResponse(2002)


@router.put("/product/id/{productId}")
async def updateProductByIdEndpoint(request: Request, productId: str, payload: ProductImportModel):
    try:
        logger.debug(f"updateProductByIdEndpoint function started for productId: {productId}")
        userId = request.state.userMetadata.get("id")

        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized update attempt by user [{userId}] on product ID: {productId}")
            return returnResponse(2000)

        logger.info(f"User [{userId}] attempting to update product with ID: {productId}")

        existing = getProductFromDb({"id": productId, "isDeleted": False})
        if not existing:
            logger.warning(f"No product found with ID: {productId}")
            return returnResponse(2003)

        updatePayload = payload.model_dump()
        updatePayload.update(
            {
                "id": productId,
                "slug": slugify(payload.slug or payload.name),
                "updatedAt": formatDateTime(),
                "createdBy": existing.get("createdBy", userId),
                "createdAt": existing.get("createdAt", formatDateTime()),
                "isDeleted": False,
            }
        )

        updateProductInDb({"id": productId}, updatePayload)
        logger.info(f"Product [ID: {productId}] updated successfully by user [{userId}]")

        updatePayload.pop("_id", None)
        return returnResponse(2018, result=updatePayload)

    except Exception as e:
        logger.error(f"Failed to update product [ID: {productId}] by user [{userId}]: {str(e)}")
        return returnResponse(2019)


@router.delete("/product/deleteProducts")
async def deleteProducts(request: Request):
    try:
        logger.debug("deleteProducts function started")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access attempt to delete products")
            return returnResponse(2000)
        result = updateManyProductsInDb({"isDeleted": False}, {"isDeleted": True})
        deletedCount = result.modified_count
        logger.info(f"Soft-deleted {deletedCount} products")
        return returnResponse(2008 if deletedCount else 2007, result={"deleted": deletedCount})
    except Exception as e:
        logger.error(f"Error deleting products: {e}")
        return returnResponse(2009)


@router.delete("/product/{productId}")
async def deleteProductById(request: Request, productId: str):
    try:
        logger.debug(f"Deleting product: {productId}")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            return returnResponse(2000)
        product = getProductFromDb({"id": productId, "isDeleted": False})
        if not product:
            logger.warning(f"Product with ID :{productId} not found or already deleted")
            return returnResponse(2016)
        result = updateProductInDb({"id": productId}, {"isDeleted": True})
        return returnResponse(2015 if result.modified_count else 2016, result={"deleted": result.modified_count})
    except Exception as e:
        logger.error(f"Error deleting product [{productId}]: {e}")
        return returnResponse(2017)


# @router.put("/product/{productId}/stock")
# async def updateStock(request: Request, productId: str, payload: dict = Body(...)):
#     try:
#         userId = request.state.userMetadata.get("id")
#         if not hasRequiredRole(request, [UserRoles.Admin.value]):
#             logger.warning(f"Unauthorized stock update by user [{userId}]")
#             return returnResponse(2000)

#         quantity = payload.get("quantity", 0)
#         stockStatus = quantity > 0

#         updateProductInDb({"id": productId, "isDeleted": False}, {"noOfProducts": quantity, "inStock": stockStatus})
#         logger.info(f"Stock updated for product [{productId}] to {quantity} by user [{userId}]")
#         return returnResponse(2093)
#     except Exception as e:
#         logger.error(f"Error updating stock for product [{productId}]: {e}")
#         return returnResponse(2094)


@router.get("/stats/products")
async def getProductStats(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized access attempt by user [{userId}] to fetch product stats.")
            return returnResponse(2000)
        logger.info(f"Fetching product stats for admin [{userId}]")
        # Get non-deleted products
        products = list(getProductsFromDb({"isDeleted": False}))
        total = len(products)
        inStock = sum(1 for p in products if p.get("stock") is True)

        # Category-wise counts
        categories = {}
        for p in products:
            category = p.get("category", "Uncategorized")
            categories[category] = categories.get(category, 0) + 1

        stats = {
            "totalProducts": total,
            "inStock": inStock,
            "categories": categories,
        }

        logger.info(f"Product stats retrieved by admin [{userId}]")
        return returnResponse(2106, result=stats)
    except Exception as e:
        logger.error(f"[STATS_ERROR] Error retrieving product stats: {str(e)}")
        return returnResponse(2107)


@router.get("/stats/orders")
async def getOrderStats(request: Request):
    try:
        userId = request.state.userMetadata.get("id")

        # Authorization check
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized access attempt by user [{userId}] to fetch order stats.")
            return returnResponse(2000)

        logger.info(f"Fetching order stats for admin [{userId}]")

        # Fetch all non-deleted orders
        orders = list(getAllOrders({"isDeleted": False}))

        # Compute stats
        totalOrders = len(orders)
        pendingOrders = sum(1 for order in orders if order.get("status") == "pending")
        completedOrders = sum(1 for order in orders if order.get("status") == "completed")
        totalRevenue = sum(order.get("amount", 0) for order in orders if isinstance(order.get("amount"), (int, float)))

        stats = {"totalOrders": totalOrders, "pendingOrders": pendingOrders, "completedOrders": completedOrders, "totalRevenue": totalRevenue}

        logger.info(f"Order stats retrieved by admin [{userId}]")
        return returnResponse(2108, result=stats)

    except Exception as e:
        logger.error(f"[STATS_ERROR] Error retrieving order stats: {str(e)}")
        return returnResponse(2109)
