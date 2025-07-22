from fastapi import APIRouter, Request
from Razor_pay.Models.model import OrderRequest
from Razor_pay.Services.razorpayClient import client
from Razor_pay.Database.ordersDb import *
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from Models.userModel import UserRoles
from Utils.utils import hasRequiredRole
from yensiDatetime.yensiDatetime import formatDateTime


router = APIRouter(tags=["Order Service"])


@router.post("/order")
def createOrder(request: Request, payload: OrderRequest):
    try:
        logger.info("Initiating Razorpay order creation.")
        razorpayPayload = {"amount": payload.amount, "currency": payload.currency, "receipt": payload.receipt, "notes": payload.notes or {}}
        orderData = client.order.create(razorpayPayload)

        orderId = orderData.get("id")
        if not orderId:
            logger.warning("Razorpay returned no order ID.")
            return returnResponse(1527)
        fullOrder = {
            **orderData,
            "createdAt": formatDateTime(),
            "items": [item.model_dump() for item in payload.items] if payload.items else [],
            "shippingAddress": payload.shippingAddress.model_dump() if payload.shippingAddress else None,
            "trackingNumber":""
        }

        insertOrder(fullOrder)
        fullOrder.pop("_id", None)
        logger.info("Order created and stored successfully. orderId: %s", orderData["id"])
        return returnResponse(1526, result=fullOrder)

    except Exception as e:
        logger.error("Order creation failed,Error: %s", str(e))
        return returnResponse(1527)


@router.get("/orders/{orderId}")
def fetchOrder(request: Request, orderId: str):
    try:
        logger.info("Fetching order. orderId: %s", orderId)
        orderData = client.order.fetch(orderId)
        currentStatus = orderData.get("status")
        if not currentStatus:
            logger.warning("No status found in Razorpay response.")
            return returnResponse(1555)
        logger.debug(f"Fetched status from Razorpay: {currentStatus}")

        localOrder = getOrderById(orderId)
        if not localOrder:
            logger.warning("Local order not found.")
            return returnResponse(1556)
        if localOrder.get("status") != currentStatus:
            updateOrder({"id": orderId}, {"status": currentStatus})
            logger.info(f"Updated local order status to: {currentStatus}")

        updatedOrder = getOrderById(orderId)
        logger.info("Order fetched successfully. orderId: %s", orderId)
        return returnResponse(1528, result=updatedOrder)
    except Exception as e:
        logger.error(f"Failed to fetch order for orderId: {orderId},Error: {str(e)}")
        return returnResponse(1529)


@router.get("/orders/{orderId}/payments")
def fetchAllPaymentsForOrder(request: Request, orderId: str):
    try:
        logger.info("Fetching payments for order. orderId: %s", orderId)
        payments = client.order.payments(orderId)
        logger.info("Payments fetched successfully. orderId: %s", orderId)
        return returnResponse(1530, result=payments)
    except Exception as e:
        logger.error(f"Failed to fetch payments for orderId: {orderId} , Error : {str(e)}")
        return returnResponse(1531)


@router.get("/orderservice")
def listOrders(request: Request):
    try:
        logger.info("Fetching all orders.")
        orders = getAllOrders()
        logger.info("All orders fetched successfully.")
        return returnResponse(1532, result=orders)
    except Exception as e:
        logger.error("Failed to fetch all orders, Error: %s", str(e))
        return returnResponse(1533)


@router.get("/user/orders")
def getUserOrders(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        if not userId:
            logger.warning("Unauthorized access: userId not found in request metadata.")
            return returnResponse(1559)
        query = {"notes.userId": userId}
        logger.info(f"Fetching orders for user [{userId}]")
        orders = getAllOrders(query)
        for order in orders:
            order.pop("_id", None)
        logger.info(f"successfully fetched user Order")
        return returnResponse(1557, result=orders)
    except Exception as e:
        logger.error(f"Failed to fetch user orders. Error: {str(e)}", exc_info=True)
        return returnResponse(1558)


@router.get("/admin/orders")
def getUserOrders(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized access attempt by user [{userId}] to fetch product stats.")
            return returnResponse(2000)

        logger.info(f"Fetching orders for user [{userId}]")
        orders = getAllOrders({})
        for order in orders:
            order.pop("_id", None)
        logger.info(f"successfully fetched user Order")
        return returnResponse(1560, result=orders)
    except Exception as e:
        logger.error(f"Failed to fetch user orders. Error: {str(e)}", exc_info=True)
        return returnResponse(1561)
