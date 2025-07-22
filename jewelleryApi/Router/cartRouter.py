# routers/cartWishlistRouter.py
from bson import ObjectId
from fastapi import APIRouter, Request
from Database.cartWishlistDb import addToCartDb, getCartDb, updateCartDb, updateQuantityCartDb, getSingleCartDb, addBulkToCartDb, updateCartManyDb
from Database.productDb import getProductFromDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiDatetime.yensiDatetime import formatDateTime
from Models.cartWishlistModel import CartItemModel, BulkCartRequest

router = APIRouter(tags=["Cart & Wishlist"])


@router.post("/cart/add")
async def addToCart(request: Request, payload: CartItemModel):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Adding to cart for user:{userId}")
        cartItem = payload.model_dump()
        productId = cartItem["productId"]

        product = getProductFromDb({"id": productId})
        if not product:
            logger.warning(f"Product with ID {productId} not found.")
            return returnResponse(2003)
        cartItem.update({"id": str(ObjectId()), "userId": userId, "createdAt": formatDateTime(), "isDeleted": False, "productId": productId, "product": product})
        addToCartDb(cartItem)
        cartItem.pop("_id", None)
        logger.info(f"cartItem added sussessfully")
        return returnResponse(2060, result=cartItem)
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return returnResponse(2062)


@router.get("/cart")
async def getCart(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"feetching cart fo use :{userId}")
        cart = list(getCartDb({"userId": userId, "isDeleted": False}))
        return returnResponse(2061, result=cart)
    except Exception as e:
        logger.error(f"Error fetching cart: {e}")
        return returnResponse(2062)


@router.put("/cart/update/{cartId}")
async def updateCartItem(request: Request, cartId: str, quantity: int):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Attempting to update cart item [{cartId}] for user [{userId}]")
        cartItem = getSingleCartDb({"id": cartId, "isDeleted": False})
        if not cartItem:
            logger.warning(f"cart Item not found to update with Id:{cartId}")
            return returnResponse(2119)
        current_quantity = cartItem.get("quantity", 0)
        newQuantity = current_quantity + quantity  # quantity = -1 here
        if newQuantity < 1:
            logger.warning(f"cannot decrease. quantity already at minimum")
            return returnResponse(2131)
        query = {"id": cartId, "userId": userId, "isDeleted": False}
        updateQuantityCartDb(query, {"$inc": {"quantity": quantity}})
        cartData = getSingleCartDb({"id": cartId, "isDeleted": False})
        logger.info(f"Quantity updated for cart item [{cartId}] for user [{userId}]")
        return returnResponse(2120, result=cartData)
    except Exception as e:
        logger.error(f"Error updating quantity for cart item [{cartId}]: {e}", exc_info=True)
        return returnResponse(2121)


@router.delete("/cart/remove/{cartId}")
async def removeCartItem(request: Request, cartId: str):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Attempting to remove cart item [{cartId}] for user [{userId}]")
        query = {"id": cartId, "userId": userId, "isDeleted": False}
        updateData = {"isDeleted": True, "deletedAt": formatDateTime()}
        result = updateCartDb(query, updateData)
        if result.modified_count == 0:
            logger.warning(f"No active cart item found with id [{cartId}] for user [{userId}]")
            return returnResponse(2116)
        cartData = getSingleCartDb({"id": cartId, "isDeleted": False})
        logger.info(f"Cart item [{cartId}] marked as deleted for user [{userId}]")
        return returnResponse(2117, result=cartData)
    except Exception as e:
        logger.error(f"Error deleting cart item [{cartId}]: {e}", exc_info=True)
        return returnResponse(2118)


@router.post("/cart/merge")
async def mergeToCart(request: Request, payload: BulkCartRequest):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Bulk cart add started by user [{userId}]")
        print(payload.model_dump())

        cartItems = []

        for item in payload.items:
            # If product is not embedded in request, fetch from DB
            product = item.product or getProductFromDb({"id": item.productId, "isDeleted": False})

            if not product:
                logger.warning(f"Product with ID [{item.productId}] not found. Skipping item.")
                continue

            cartItem = {
                "id": str(ObjectId()),
                "userId": userId,
                "productId": item.productId,
                "quantity": item.quantity,
                "product": product.model_dump() if hasattr(product, "model_dump") else product,
                "isDeleted": False,
                "createdAt": formatDateTime(),
            }
            cartItems.append(cartItem)

        if not cartItems:
            logger.warning(f"No valid cart items to add for user [{userId}].")
            return returnResponse(2134)

        addBulkToCartDb(cartItems)
        logger.info(f" cart items added successfully for user [{userId}]")
        return returnResponse(2132)

    except Exception as e:
        logger.error(f"Error adding cart items in bulk for user [{userId}]: {e}", exc_info=True)
        return returnResponse(2133)


@router.delete("/cart/clear")
async def clearAllCartItems(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        logger.debug(f"Attempting to clear all cart items for user [{userId}]")

        query = {"userId": userId, "isDeleted": False}
        updateData = {"isDeleted": True, "deletedAt": formatDateTime()}
        result = updateCartManyDb(query, updateData)

        if result.modified_count == 0:
            logger.warning(f"No active cart items found to clear for user [{userId}]")
            return returnResponse(2116)

        logger.info(f"{result.modified_count} cart items cleared for user [{userId}]")
        return returnResponse(2070)

    except Exception as e:
        logger.error(f"Error clearing cart items for user [{userId}]: {e}", exc_info=True)
        return returnResponse(2071)
