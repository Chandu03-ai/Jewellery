from typing import Optional
from fastapi import APIRouter, Depends, Request
from Razor_pay.Services.razorpayClient import client
from Razor_pay.Database.ordersDb import *
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from Razor_pay.Database.paymentsDb import *
from Razor_pay.Database.invoiceDb import *
from Razor_pay.Utils.util import getCustomerId
router = APIRouter(prefix="/payments", tags=["Payment Service"])


@router.get("/history")
def getPaymentHistory(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        customerId = getCustomerId(request)

        payments = listPayments({"customerId": customerId})
        logger.info(f"Retrieved payments for user {userId}")

        return returnResponse(1553, result=payments)
    except Exception as e:
        logger.error(f"Error retrieving payment history: {str(e)}")
        return returnResponse(1554)

@router.get("/invoice/{paymentId}")
def getInvoiceUsingPaymentId(paymentId: str):
    try:
        logger.info(f"Fetching invoice for payment ID: {paymentId}")
        payment = getPaymentById(paymentId)
        invoiceId = payment.get("invoiceId")

        if not invoiceId:
            logger.warning(f"No invoice linked to payment {paymentId}")
            return returnResponse(1555, result={"message": "No invoice linked."})

        invoice = getInvoiceFromDb({"invoiceId": invoiceId})
        logger.info(f"Invoice PDF link fetched for invoice {invoiceId}")
        return returnResponse(1556, result=invoice)
    except Exception as e:
        logger.error(f"Error fetching invoice for payment {paymentId}: {str(e)}")
        return returnResponse(1557)

