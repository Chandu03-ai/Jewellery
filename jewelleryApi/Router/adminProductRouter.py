# routers/adminProductRouter.py
from bson import ObjectId
from fastapi import APIRouter, Body, Request, File, UploadFile, HTTPException
from Models.productModel import ProductImportModel
from Database.productDb import getProductsFromDb, updateManyProductsInDb, insertProductToDb, getProductFromDb, updateProductInDb, insertImportHistoryToDb
from Utils.utils import buildCategoryDocument, hasRequiredRole, buildTagDocument
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse
import json
import pandas as pd
from io import BytesIO

from Razor_pay.Database.ordersDb import getAllOrders

router = APIRouter(prefix="/admin", tags=["Admin-Products"])


@router.post("/products/bulk-upload")
async def importProductsFromFile(request: Request, file: UploadFile = File(...)):
    userId = request.state.userMetadata.get("id")

    if not hasRequiredRole(request, [UserRoles.Admin.value]):
        logger.warning(f"[IMPORT_DENIED] Unauthorized user [{userId}] attempted product import.")
        return returnResponse(2000)

    try:
        logger.info(f"[IMPORT_START] Reading uploaded file: {file.filename}")
        content = await file.read()

        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(content))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(content))
        else:
            errorMsg = f"Unsupported file format: {file.filename}. Only .csv and .xlsx are supported."
            logger.error(f"[IMPORT_FAIL] {errorMsg}")
            raise HTTPException(status_code=400, detail=errorMsg)

        records = df.to_dict(orient="records")

        listFields = ["images", "tags", "seoKeywords", "relatedProducts"]
        jsonFields = ["specifications", "variants", "dimensions"]
        cleanedRecords = []

        for rec in records:
            # Handle list fields (semi-colon separated)
            for field in listFields:
                value = rec.get(field)
                if isinstance(value, str):
                    rec[field] = [item.strip() for item in value.split(";") if item.strip()]
                elif value is None:
                    rec[field] = []

            if "tags" in rec and isinstance(rec["tags"], str):
                tagList = [tag.strip() for tag in rec["tags"].split(";") if tag.strip()]
                colorList = [color.strip() for color in rec.get("tagColors", "").split(";")]
            
                rec["tags"] = []
                for i, tag in enumerate(tagList):
                    tagData = {"name": tag}
                    if i < len(colorList):
                        tagData["color"] = colorList[i]
                    rec["tags"].append(tagData)

            # Handle JSON fields if they exist
            for field in jsonFields:
                value = rec.get(field)
                if isinstance(value, str):
                    try:
                        rec[field] = json.loads(value)
                    except json.JSONDecodeError:
                        logger.warning(f"[PARSING_WARNING] Invalid JSON in field '{field}' for product {rec.get('name')}. Using fallback.")
                        rec[field] = {}

            # Build specifications manually from dot-notated columns
            rec["specifications"] = {
                "material": rec.pop("specifications.material", ""),
                "weight": rec.pop("specifications.weight", ""),
                "dimensions": rec.pop("specifications.dimensions", ""),
                "gemstone": rec.pop("specifications.gemstone", ""),
            }

            # Build dimensions manually from dot-notated columns
            rec["dimensions"] = {
                "length": float(rec.pop("dimensions.length", 0) or 0),
                "width": float(rec.pop("dimensions.width", 0) or 0),
                "height": float(rec.pop("dimensions.height", 0) or 0),
                "weight": float(rec.pop("dimensions.weight", 0) or 0),
            }

            cleanedRecords.append(rec)

        payload = []
        for rec in cleanedRecords:
            try:
                payload.append(ProductImportModel(**rec))
            except Exception as e:
                logger.error(f"[VALIDATION_ERROR] Skipping invalid product record: {rec.get('name', 'Unnamed')} - {e}")

    except Exception as e:
        logger.exception(f"[IMPORT_ERROR] Failed to parse file: {e}")
        return returnResponse(2102)

    total, imported, updated, failed = len(payload), 0, 0, 0
    processedProducts = []

    for product in payload:
        try:
            logger.debug(f"[PROCESS_PRODUCT] Processing: {product.name}")
            buildCategoryDocument(product.category)
            buildTagDocument(product.tags)

            slug = slugify(product.name)
            productDict = product.model_dump()
            productDict.update({"slug": slug, "updatedAt": formatDateTime()})

            existing = getProductFromDb({"slug": slug})

            if existing:
                productDict["id"] = existing["id"]
                productDict["noOfProducts"] = existing.get("noOfProducts", 0) + product.noOfProducts
                updateProductInDb({"slug": slug}, productDict)
                updated += 1
                logger.info(f"[PRODUCT_UPDATED] {product.name} (slug: {slug}) - Quantity updated.")
            else:
                productDict.update({"id": str(ObjectId()), "createdBy": userId, "createdAt": formatDateTime(), "isDeleted": False})
                insertProductToDb(productDict)
                imported += 1
                logger.info(f"[PRODUCT_INSERTED] {product.name} (slug: {slug}) - New product added.")

            productDict.pop("_id", None)
            processedProducts.append(productDict)

        except Exception as e:
            failed += 1
            logger.exception(f"[PRODUCT_ERROR] Failed to import/update: {product.name} - {e}")

    try:
        insertImportHistoryToDb(
            {"id": str(ObjectId()), "userId": userId, "fileName": file.filename, "timestamp": formatDateTime(), "total": total, "imported": imported, "updated": updated, "failed": failed}
        )
    except Exception as e:
        logger.exception(f"[HISTORY_ERROR] Failed to record import history - {e}")

    logger.info(f"[IMPORT_COMPLETE] User [{userId}] finished import. Total: {total}, Inserted: {imported}, Updated: {updated}, Failed: {failed}")
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

        existing = getProductFromDb({"id": productId, "isDeleted": False})
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


@router.put("/product/{productId}/stock")
async def updateStock(request: Request, productId: str, payload: dict = Body(...)):
    try:
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized stock update by user [{userId}]")
            return returnResponse(2000)

        quantity = payload.get("quantity", 0)
        stockStatus = quantity > 0

        updateProductInDb({"id": productId, "isDeleted": False}, {"noOfProducts": quantity, "inStock": stockStatus})
        logger.info(f"Stock updated for product [{productId}] to {quantity} by user [{userId}]")
        return returnResponse(2093)
    except Exception as e:
        logger.error(f"Error updating stock for product [{productId}]: {e}")
        return returnResponse(2094)


@router.post("/product/create")
async def createProduct(request: Request, payload: ProductImportModel):
    try:
        userId = request.state.userMetadata.get("id")

        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized access attempt by user [{userId}] to import product.")
            return returnResponse(2000)

        logger.info(f"Starting single product import by user [{userId}] for product: {payload.name}")

        buildCategoryDocument(payload.category)
        buildTagDocument(payload.tags)

        slug = slugify(payload.name)
        productDict = payload.model_dump()
        productDict.update({"slug": slug, "updatedAt": formatDateTime()})

        existing = getProductFromDb({"slug": slug, "isDeleted": False})

        if existing:
            productDict["id"] = existing["id"]
            productDict["noOfProducts"] = existing.get("noOfProducts", 0) + payload.noOfProducts
            updateProductInDb({"slug": slug, "isDeleted": False}, productDict)
            logger.info(f"Updated existing product quantity: {payload.name} (slug: {slug})")
        else:
            productDict.update({"id": str(ObjectId()), "createdBy": userId, "createdAt": formatDateTime(), "isDeleted": False})
            insertProductToDb(productDict)
            logger.info(f"Inserted new product: {payload.name} (slug: {slug})")

        productDict.pop("_id", None)

        insertImportHistoryToDb(
            {
                "id": str(ObjectId()),
                "userId": userId,
                "fileName": "frontend-payload",
                "timestamp": formatDateTime(),
                "total": 1,
                "imported": 1 if not existing else 0,
                "updated": 1 if existing else 0,
                "failed": 0,
            }
        )

        logger.info(f"Single product import completed by user [{userId}].")
        return returnResponse(2103, result=productDict)

    except Exception as e:
        logger.error(f"[IMPORT_ERROR] Error importing product [{payload.name}]: {str(e)}")
        return returnResponse(2104)


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
        inStock = sum(1 for p in products if p.get("inStock") is True)
        outOfStock = sum(1 for p in products if p.get("inStock") is False)
        featured = sum(1 for p in products if p.get("featured") is True)

        # Category-wise counts
        categories = {}
        for p in products:
            category = p.get("category", "Uncategorized")
            categories[category] = categories.get(category, 0) + 1

        stats = {
            "totalProducts": total,
            "inStock": inStock,
            "outOfStock": outOfStock,
            "featured": featured,
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
        return returnResponse(2018, result=stats)

    except Exception as e:
        logger.error(f"[STATS_ERROR] Error retrieving order stats: {str(e)}")
        return returnResponse(2019)
