from bson import ObjectId
from fastapi import APIRouter, Request
from Database.shippingDb import getShipmentFromDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from Models.shipmentModel import ShipmentModel
from Models.userModel import UserRoles
from Utils.utils import hasRequiredRole
from Razor_pay.Database.ordersDb import getOrderById, updateOrder


router = APIRouter()


@router.post("/admin/send-tracking")
async def addShipment(request: Request, payload: ShipmentModel):
    try:
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to update category")
            return returnResponse(2000)
        orderId = payload.orderId
        trackingNumber = payload.trackingNumber
        orderData = getOrderById(orderId)
        if not orderData:
            logger.warning(f"Order not found or already completed for orderId: {orderId}")
            return returnResponse(2125)
        updateOrder({"id": orderId}, {"trackingNumber": trackingNumber})
        logger.info(f"order updated with trackingNumber [{trackingNumber}] for orderId [{orderId} entred by admin :{userId}]")
        return returnResponse(2126)
    except Exception as e:
        logger.error(f"Error adding shipment: {e}", exc_info=True)
        return returnResponse(2127)


