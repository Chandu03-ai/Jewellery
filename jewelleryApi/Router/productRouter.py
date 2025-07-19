# routers/productRouter.py
from typing import List, Optional
from fastapi import APIRouter, Query
from Database.productDb import getProductsFromDb, getProductFromDb, updateProductInDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse

router = APIRouter(prefix="/public", tags=["Products"])


@router.get("/products")
async def getProducts():
    try:
        logger.debug(f"fetching all products")
        products = list(getProductsFromDb({"isDeleted": False}))
        logger.info(f"fetched all products successfully")
        return returnResponse(2005, result=products if products else [])
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return returnResponse(2004)


# @router.get("/products/filter")
# async def filterProducts(category: Optional[str] = None, priceMin: Optional[float] = None, priceMax: Optional[float] = None, tags: Optional[List[str]] = Query(None)):

#     try:
#         logger.debug(f"filterProducts function started")
#         query = {"isDeleted": False}
#         if category:
#             query["category"] = category
#         if priceMin is not None or priceMax is not None:
#             query["price"] = {}
#             if priceMin is not None:
#                 query["price"]["$gte"] = priceMin
#             if priceMax is not None:
#                 query["price"]["$lte"] = priceMax
#         if tags:
#             query["tags"] = {"$in": tags}

#         products = list(getProductsFromDb(query))
#         logger.info(f"filtered products successfully with criteria: {query}")
#         return returnResponse(2005, result=products)
#     except Exception as e:
#         logger.error(f"Error filtering products: {e}")
#         return returnResponse(2004)



@router.get("/products/search")
async def searchProducts(q: str):
    try:
        logger.debug(f"Searching products for query: {q}")
        query = {
            "$or": [
                {"isDeleted": False},
                {"name": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
                {"tags": {"$in": [q]}},
            ]
        }
        products = list(getProductsFromDb(query))
        suggestions = [{"query": q, "type": "product", "count": len(products)}]
        return returnResponse(2089, result={"products": products, "total": len(products), "suggestions": suggestions})
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return returnResponse(2090)


@router.get("/products/suggestions")
async def getSearchSuggestions(q: str):
    try:
        logger.debug(f"Getting suggestions for query: {q}")
        query = {
            "$or": [
                {"isDeleted": False},
                {"name": {"$regex": q, "$options": "i"}},
                {"category": {"$regex": q, "$options": "i"}},
                {"tags": {"$in": [q]}},
            ]
        }
        products = list(getProductsFromDb(query))
        suggestions = [{"query": q, "type": "product", "count": len(products)}]
        return returnResponse(2091, result=suggestions)
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        return returnResponse(2092)


@router.get("/products/{slug}")
async def getProductBySlug(slug: str):
    try:
        logger.debug(f"getProductBySlug function started ")
        product = getProductFromDb({"slug": slug, "isDeleted": False})
        if not product:
            return returnResponse(2010, result=None)
        logger.info(f"Product fetched successfully by slug: {slug}")
        return returnResponse(2005, result=product)
    except Exception as e:
        logger.error(f"Error fetching product by slug: {e}")
        return returnResponse(2004)
