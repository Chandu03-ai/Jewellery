# routers/productRouter.py
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Body, Request, Query
from Models.productModel import ProductImportModel
from Database.productDb import insertProductToDb, getProductsFromDb, getProductFromDb, updateProductInDb, deleteProductFromDb, deleteProductsFromDb, insertImportHistoryToDb
from Database.categoryDb import insertCategoryIfNotExists
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime
from Models.userModel import UserRoles
from yensiAuthentication import logger
from Utils.slugify import slugify
from ReturnLog.logReturn import returnResponse

router = APIRouter(prefix="/public",tags=["Products"])



@router.get("/products")
async def getProducts():
    try:
        logger.debug(f"fetching all products")
        products = list(getProductsFromDb())

        for product in products:
            noOfProducts = product.get("noOfProducts", 0)
            currentInStock = product.get("inStock", True)

            if noOfProducts <= 0 and currentInStock is not False:
                product["inStock"] = False
                updateProductInDb({"slug": product["slug"]}, {"inStock": False})
                logger.info(f"Updated inStock=False for product: {product['name']} due to zero stock")
        logger.info(f"fetched all products successfully")
        return returnResponse(2005, result=products if products else [])
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return returnResponse(2004)


@router.get("/products/filter")
async def filterProducts(category: Optional[str] = None, priceMin: Optional[float] = None, priceMax: Optional[float] = None, tags: Optional[List[str]] = Query(None)):

    try:
        logger.debug(f"filterProducts function started")
        query = {}
        if category:
            query["category"] = category
        if priceMin is not None or priceMax is not None:
            query["price"] = {}
            if priceMin is not None:
                query["price"]["$gte"] = priceMin
            if priceMax is not None:
                query["price"]["$lte"] = priceMax
        if tags:
            query["tags"] = {"$in": tags}

        products = list(getProductsFromDb(query))
        logger.info(f"filtered products successfully with criteria: {query}")
        return returnResponse(2005, result=products)
    except Exception as e:
        logger.error(f"Error filtering products: {e}")
        return returnResponse(2004)


@router.get("/products/{slug}")
async def getProductBySlug(slug: str):
    try:
        logger.debug(f"getProductBySlug function started ")
        product = getProductFromDb({"slug": slug})
        if not product:
            return returnResponse(2010, result=None)
        logger.info(f"Product fetched successfully by slug: {slug}")
        return returnResponse(2005, result=product)
    except Exception as e:
        logger.error(f"Error fetching product by slug: {e}")
        return returnResponse(2004)



@router.get("/products/featured")
async def getFeaturedProducts():
    try:
        logger.debug("Fetching featured products")
        featured = list(getProductsFromDb({"featured": True}))
        return returnResponse(2085, result=featured)
    except Exception as e:
        logger.error(f"Error fetching featured products: {e}")
        return returnResponse(2086)


@router.get("/products/by-tag/{tag}")
async def getProductsByTag(tag: str):
    try:
        logger.debug(f"Fetching products with tag: {tag}")
        taggedProducts = list(getProductsFromDb({"tags": tag}))
        return returnResponse(2087, result=taggedProducts)
    except Exception as e:
        logger.error(f"Error fetching products by tag: {e}")
        return returnResponse(2088)


@router.get("/products/search")
async def searchProducts(q: str):
    try:
        logger.debug(f"Searching products for query: {q}")
        query = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"category": {"$regex": q, "$options": "i"}},
            {"tags": {"$in": [q]}},
        ]}
        products = list(getProductsFromDb(query))
        suggestions = [
            {"query": q, "type": "product", "count": len(products)}
        ]
        return returnResponse(2089, result={"products": products, "total": len(products), "suggestions": suggestions})
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return returnResponse(2090)


@router.get("/products/suggestions")
async def getSearchSuggestions(q: str):
    try:
        logger.debug(f"Getting suggestions for query: {q}")
        query = {"$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"category": {"$regex": q, "$options": "i"}},
            {"tags": {"$in": [q]}},
        ]}
        products = list(getProductsFromDb(query))
        suggestions = [
            {"query": q, "type": "product", "count": len(products)}
        ]
        return returnResponse(2091, result=suggestions)
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        return returnResponse(2092)




# Stub endpoints for reviews (assume models and DB logic are elsewhere)
@router.get("/products/{productId}/reviews")
async def getProductReviews(productId: str):
    try:
        # Dummy fetch logic placeholder
        logger.debug(f"Fetching reviews for product [{productId}]")
        return returnResponse(2095, result=[])
    except Exception as e:
        logger.error(f"Failed to fetch reviews for [{productId}]: {e}")
        return returnResponse(2096)


@router.post("/products/{productId}/reviews")
async def addProductReview(request: Request, productId: str, payload: dict = Body(...)):
    try:
        # Dummy insert logic placeholder
        userId = request.state.userMetadata.get("id")
        logger.debug(f"User [{userId}] adding review to product [{productId}]")
        return returnResponse(2097, result=payload)
    except Exception as e:
        logger.error(f"Failed to add review: {e}")
        return returnResponse(2098)
