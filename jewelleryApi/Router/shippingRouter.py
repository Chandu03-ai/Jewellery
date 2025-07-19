from fastapi import APIRouter, Request
from Models.shippingModel import ShipmentRequestModel
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiDatetime.yensiDatetime import formatDateTime
from uuid import uuid4
from Database.shippingDb import createShipmentDb, getShipmentDb, updateShipmentStatusDb

router = APIRouter(tags=["Shipping"])

@router.post("/shipping/create-shipment")
async def createShipment(request: Request, payload: ShipmentRequestModel):
    try:
        userId = request.state.userMetadata.get("id")
        awb = f"D{uuid4().hex[:8].upper()}"
        shipment = payload.model_dump()
        shipment.update({
            "awbNumber": awb,
            "userId": userId,
            "labelUrl": f"https://mock.dtdc.com/labels/{awb}.pdf",
            "createdAt": formatDateTime(),
            "status": "Booked"
        })
        createShipmentDb(shipment)
        logger.info(f"Shipment created: {awb}")
        return returnResponse(1800, result=shipment)
    except Exception as e:
        logger.error(f"Error in createShipment: {e}")
        return returnResponse(1806)

@router.get("/shipping/track/{awb}")
async def trackShipment(awb: str):
    try:
        shipment = getShipmentDb(awb)
        if not shipment:
            return returnResponse(1805)
        return returnResponse(1803, result={"awbNumber": awb, "status": shipment["status"]})
    except Exception as e:
        logger.error(f"Error in trackShipment: {e}")
        return returnResponse(1806)

@router.post("/shipping/cancel/{awb}")
async def cancelShipment(awb: str):
    try:
        shipment = getShipmentDb(awb)
        if not shipment:
            return returnResponse(1805)
        updateShipmentStatusDb(awb, "Cancelled")
        return returnResponse(1801, result={"awbNumber": awb})
    except Exception as e:
        logger.error(f"Error in cancelShipment: {e}")
        return returnResponse(1806)

@router.get("/shipping/label/{awb}")
async def getLabel(awb: str):
    try:
        shipment = getShipmentDb(awb)
        if not shipment:
            return returnResponse(1805)
        return returnResponse(1802, result={"labelUrl": shipment["labelUrl"]})
    except Exception as e:
        logger.error(f"Error in getLabel: {e}")
        return returnResponse(1806)

@router.get("/shipping/history/{awb}")
async def shipmentHistory(awb: str):
    try:
        shipment = getShipmentDb(awb)
        if not shipment:
            return returnResponse(1805)
        return returnResponse(1804, result={
            "awbNumber": awb,
            "history": [
                {"status": "Booked", "location": "Bangalore", "time": "2025-07-18 10:00"},
                {"status": "In Transit", "location": "Hub", "time": "2025-07-18 20:00"},
                {"status": shipment["status"], "location": "Destination", "time": "2025-07-19 14:00"}
            ]
        })
    except Exception as e:
        logger.error(f"Error in shipmentHistory: {e}")
        return returnResponse(1806)
