from fastapi import APIRouter
from ReturnLog.logReturn import returnResponse
from yensiEmailService.gmail import sendEmail
from yensiAuthentication import logger
from yensiDatetime.yensiDatetime import formatDateTime
from Utils.emailUtility import loadHtmlTemplate
from Database.emailDb import insertData
from Models.emailModel import OrderSuccessEmailRequest, RegisterSuccessEmailRequest

router = APIRouter()


@router.post("/auth/sendEmail")
async def sendEmailUser(payload: RegisterSuccessEmailRequest):
    try:
        email = payload.email
        logger.info(f"Sending OTP to {email}")
        sentTime = formatDateTime()
        subject = "User Registred Successfully"
        templatePath = "Templates/registerSuccess.html"
        htmlBody = loadHtmlTemplate(templatePath, {"userName": payload.userName})
        sendEmail(email, subject=subject, body=htmlBody, isHtml=True)
        logger.info(f"Email sent successfully to {email}")
        otpData = {"email": email, "sentAt": sentTime, "status": "sent"}
        insertData(otpData)
        return returnResponse(2147)
    except Exception as e:
        logger.error(f"Error sending email to {email}: {e}")
        return returnResponse(2148)


@router.post("/sendOrderSuccessEmail")
async def sendOrderSuccessEmail(payload: OrderSuccessEmailRequest):
    try:
        logger.info(f"Sending order confirmation email to {payload.email}")
        sentTime = formatDateTime()
        subject = " Order Confirmation"
        templatePath = "Templates/orderSuccess.html"
        htmlBody = loadHtmlTemplate(templatePath, {"userName": payload.userName, "orderId": payload.orderId})
        sendEmail(toEmail=payload.email, subject=subject, body=htmlBody, isHtml=True)
        insertData({"email": payload.email, "sentAt": sentTime, "orderId": payload.orderId, "type": "order-success", "status": "sent"})
        return returnResponse(2147)
    except Exception as e:
        logger.error(f"Failed to send order email: {e}")
        return returnResponse(2148)
