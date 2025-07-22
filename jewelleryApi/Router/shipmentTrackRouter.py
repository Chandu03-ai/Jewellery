from bson import ObjectId
from fastapi import APIRouter, Request
from Database.shippingDb import createShipmentDb, getShipmentFromDb
from Database.productDb import getProductFromDb
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiDatetime.yensiDatetime import formatDateTime
from Models.shipmentModel import ShipmentModel
from Models.userModel import UserRoles
from Utils.utils import hasRequiredRole
from Razor_pay.Database.ordersDb import getOrderById

router = APIRouter()


@router.post("/shipment/add")
async def addShipment(request: Request, payload: ShipmentModel):
    try:
        userId = request.state.userMetadata.get("id")
        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning("Unauthorized access to update category")
            return returnResponse(2000)
        orderId = payload.orderId
        orderData = getOrderById(orderId)
        if not orderData or orderData.get("status") == "completed":
            logger.warning(f"Order not found or already completed for orderId: {orderId}")
            return returnResponse(2125)
        shipmentData = payload.model_dump()
        shipmentData.update({"id": str(ObjectId()), "createdBy": userId, "createdAt": formatDateTime(), "isDeleted": False})
        shipmentResult = createShipmentDb(shipmentData)
        logger.info(f"Shipment entry added by admin [{userId}]: {shipmentData}")
        return returnResponse(2126, result=shipmentResult)
    except Exception as e:
        logger.error(f"Error adding shipment: {e}", exc_info=True)
        return returnResponse(2127)


@router.get("/shipment/id/{shipmentId}")
async def getShipmentById(request: Request, shipmentId: str):
    try:
        userId = request.state.userMetadata.get("id")

        if not hasRequiredRole(request, [UserRoles.Admin.value]):
            logger.warning(f"Unauthorized attempt to fetch shipment by user [{userId}]")
            return returnResponse(2000)

        shipmentData = getShipmentFromDb({"id": shipmentId})
        if not shipmentData:
            logger.warning(f"No shipment found for shipmentId: {shipmentId}")
            return returnResponse(2128)
        return returnResponse(2129, result=shipmentData)
    except Exception as e:
        logger.error(f"Error fetching shipment for shipmentId [{shipmentId}]: {e}", exc_info=True)
        return returnResponse(2130)
