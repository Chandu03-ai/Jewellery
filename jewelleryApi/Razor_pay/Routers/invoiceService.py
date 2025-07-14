from fastapi import APIRouter, Request
from Razor_pay.Services.razorpayClient import client
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse
from yensiAuthentication.mongoData import updateUser
from Razor_pay.Database.invoiceDb import *
from Razor_pay.Utils.util import getCustomerId
router = APIRouter(tags=["Invoice Service"])


@router.get("/invoices/{subscriptionId}")
def getInvoicesForSubscription(request: Request, subscriptionId: str):
    try:
        logger.info(f"Fetching invoices for subscription ID: {subscriptionId}")
        invoices = getInvoiceFromDb({"subscriptionId": subscriptionId})

        # invoices = client.invoice.all({"subscription_id": subscriptionId})

        logger.info(f"Found invoice(s) for subscription {subscriptionId}")
        return returnResponse(1556, result=invoices)

    except Exception as e:
        logger.error(f"Failed to fetch invoices for subscription {subscriptionId}. Error: {str(e)}")
        return returnResponse(1557)
 

@router.get("/invoice/{invoiceId}")
def getInvoiceByInvoiceId(request: Request, invoiceId: str):
    try:
        logger.info(f"Fetching invoice with ID: {invoiceId}")
        invoice = getInvoiceFromDb({"invoiceId": invoiceId})

        # invoice = client.invoice.fetch(invoiceId)
        return returnResponse(1571, result=invoice)

    except Exception as e:
        logger.error(f"Failed to fetch invoice {invoiceId}. Error: {str(e)}")
        return returnResponse(1572)


@router.get("/invoices")
def getAllInvoices(request: Request):
    try:
        logger.info("Invoice fetch request received")
        customerId = getCustomerId(request)
        if not customerId:
            logger.warning("Customer ID missing in user metadata")
            return returnResponse(1574)

        invoices = getAllInvoicesFromDb({"customerId": customerId})
        logger.info("Invoice fetch successful")
        return returnResponse(1573, result=invoices)

    except Exception as e:
        logger.error("Invoice fetch failed")
        return returnResponse(1574)


@router.post("/invoice/notify/{invoiceId}/{medium}")
def notifyInvoice(request: Request, invoiceId: str, medium: str):
    try:
        logger.info("Invoice notification request received")

        if medium not in ["email", "sms"]:
            logger.warning("Invalid notification medium")
            return returnResponse(1577)

        logger.info("Fetching invoice to check status")
        invoice = client.invoice.fetch(invoiceId)

        if invoice.get("status") in ["paid", "cancelled", "expired"]:
            logger.warning("Notification not allowed due to invoice status")
            return returnResponse(1578)

        logger.info("Attempting to send invoice notification")
        result = client.invoice.notify_by(invoiceId, medium)

        logger.info("Invoice notification sent successfully")
        return returnResponse(1575, result=result)

    except Exception as e:
        logger.error("Invoice notification failed")
        return returnResponse(1576)
