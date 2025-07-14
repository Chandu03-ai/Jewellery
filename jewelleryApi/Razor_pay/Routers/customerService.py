from fastapi import APIRouter, HTTPException, Request
from Razor_pay.Models.model import CustomerRequest
from Razor_pay.Services.razorpayClient import client
from Razor_pay.Database.customerDb import * 
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from yensiAuthentication.mongoData import updateUser
router = APIRouter(tags=["Customer Service"])

@router.post("/customer")
async def createCustomer(request:Request,custRequest: CustomerRequest):
    try:
        userId = request.state.userMetadata.get("id")
        username = request.state.userMetadata.get("username")
        email = request.state.userMetadata.get("email")
        contact = request.state.userMetadata.get("contact")

        logger.info("Creating new customer.")
        customer = client.customer.create({
            "name": custRequest.name if custRequest.name else username,
            "email": custRequest.email if custRequest.email else email,
            "contact": custRequest.contact if custRequest.contact else contact,
            "fail_existing": custRequest.fail_existing,
            "notes": custRequest.notes or {}
        })
        logger.info("Customer created on Razorpay.")
        custData = {
            "name": customer["name"],
            "contact": customer["contact"],
            "email": customer["email"],
            "notes": customer.get("notes", {}),
            "customerId": customer["id"]
        }
        insertCustomerData(custData)
        custData.pop("_id", None)
        updateUser({"id":userId},{"userMetadata.paymentSubscription.customerId": custData["customerId"]})

        logger.info("Customer saved to database.")
        return returnResponse(1501, result=custData)
    except Exception as e:
        logger.error("Customer creation failed.,Error: %s", str(e))
        return returnResponse(1502)


@router.put("/customer/{customerId}")
async def updateCustomer(request:Request,customerId: str, custRequest: CustomerRequest):
    try:
        logger.info(f"Updating customer: {customerId}")
        customerData = getCustomerById(customerId)
        if not customerData:
            logger.warning("Customer not found in database.")
            return returnResponse(1503)

        updated_fields = {}
        for field in ["name", "contact", "email"]:
            new_value = getattr(custRequest, field, None)
            existing_value = customerData.get(field)
            if new_value is not None:
                updated_fields[field] = str(new_value) if field == "contact" else new_value
            elif existing_value is not None:
                updated_fields[field] = str(existing_value) if field == "contact" else existing_value

        if not updated_fields:
            logger.info("No fields provided for update.")
            return returnResponse(1507, result="No fields to update.")

        customer = client.customer.edit(customerId, updated_fields)
        if not customer:
            logger.warning("Customer not found on Razorpay.")
            return returnResponse(1503)

        updatedData = {
            "name": customer.get("name"),
            "contact": customer.get("contact"),
            "email": customer.get("email"),
            "notes": customer.get("notes", {})
        }

        updateCustomerData(customerId, updatedData)
        logger.info("Customer updated successfully.")
        return returnResponse(1506, result={"customerId": customer["id"], "customer": updatedData})
    except Exception as e:
        logger.error(f"Customer update failed. Error: {str(e)}")
        return returnResponse(1507)


@router.get("/customer/{customerId}")
async def fetchCustomer(request:Request,customerId: str):
    try:
        logger.info(f"Fetching customer: {customerId}")
        customerData = getCustomerById(customerId)
        if not customerData:
            logger.warning("Customer not found.")
            return returnResponse(1503)
        customerData.pop("_id", None)
        logger.info("Customer data returned.")
        return returnResponse(1504, result=customerData)
    except Exception as e:
        logger.error("Failed to fetch customer, Error: %s", str(e))
        return returnResponse(1505)


@router.get("/customers")
async def listCustomers(request:Request):
    try:
        logger.info("Fetching all customers.")
        data = getAllCustomers()
        for d in data:
            d.pop("_id", None)
        logger.info("Customer list returned.")
        return returnResponse(1508, result=data)
    except Exception as e:
        logger.error("Failed to fetch customer list, Error: %s", str(e))
        return returnResponse(1509)






