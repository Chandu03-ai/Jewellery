from fastapi import APIRouter,Request
from Razor_pay.Models.model import OrderRequest
from Razor_pay.Services.razorpayClient import client
from Razor_pay.Database.ordersDb import *
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger

router = APIRouter(tags=["Order Service"])

@router.post("/order")
def createOrder(request:Request,payload: OrderRequest):
    try:
        logger.info("Initiating Razorpay order creation.")
        orderData = client.order.create(payload.model_dump(exclude_unset=True))

        orderId = orderData.get("id")
        if not orderId:
            logger.warning("Razorpay returned no order ID.")
            return returnResponse(1527)

        orderData["orderId"] = orderData.pop("id")
        insertOrder(orderData)
        orderData.pop("_id", None)
        logger.info("Order created and stored successfully. orderId: %s", orderData["orderId"])
        return returnResponse(1526, result=orderData)

    except Exception as e:
        logger.error("Order creation failed,Error: %s", str(e))
        return returnResponse(1527)


@router.get("/orders/{orderId}")
def fetchOrder(request:Request,orderId: str):
    try:
        logger.info("Fetching order. orderId: %s", orderId)
        order = getOrderById(orderId)
        logger.info("Order fetched successfully. orderId: %s", orderId)
        return returnResponse(1528, result=order)
    except Exception as e:
        logger.error(f"Failed to fetch order for orderId: {orderId},Error: {str(e)}")
        return returnResponse(1529)


@router.get("/orders/{orderId}/payments")
def fetchAllPaymentsForOrder(request:Request,orderId: str):
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


