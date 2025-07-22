from fastapi import APIRouter, Request
from Models.addressModel import AddressModel
from Database.addressCollection import getAddressById, getUserAddressesFromDb, insertAddress, setAllDefaultFalse, updateAddress, deleteAddress
from bson import ObjectId
from yensiDatetime.yensiDatetime import formatDateTime
from yensiAuthentication import logger
from ReturnLog.logReturn import returnResponse


router = APIRouter(tags=["Address"])


@router.post("/user/addresses")
async def createAddress(request: Request, payload: AddressModel):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info(f"Creating address for user [{userId}]")

        addressDict = payload.model_dump()
        addressDict.update({"id": str(ObjectId()), "userId": userId, "createdAt": formatDateTime(), "updatedAt": formatDateTime(), "isDeleted": False})

        if addressDict["isDefault"]:
            setAllDefaultFalse(userId)

        insertAddress(addressDict)
        addressDict.pop("_id", None)
        logger.info(f"Address created for user [{userId}]")
        return returnResponse(2135, result=addressDict)
    except Exception as e:
        logger.error(f"Error creating address: {str(e)}")
        return returnResponse(2136)


@router.put("/user/addresses/{addressId}")
async def updateAddressApi(request: Request, addressId: str, payload: dict):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info(f"Updating address [{addressId}] for user [{userId}]")

        if payload.get("isDefault") is True:
            setAllDefaultFalse(userId)

        payload["updatedAt"] = formatDateTime()
        updateAddress({"id": addressId}, payload)
        updated = getAddressById({"id", addressId})
        return returnResponse(2137, result=updated)
    except Exception as e:
        logger.error(f"Error updating address [{addressId}]: {str(e)}")
        return returnResponse(2138)


@router.delete("/user/addresses/{addressId}")
async def deleteAddressApi(addressId: str):
    try:
        logger.info(f"Deleting address [{addressId}]")
        deleteAddress({"id": addressId})
        return returnResponse(2139)
    except Exception as e:
        logger.error(f"Error deleting address [{addressId}]: {str(e)}")
        return returnResponse(2140)


@router.put("/user/addresses/{addressId}/default")
async def setDefaultAddress(request: Request, addressId: str):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info(f"Setting default address for user [{userId}] to [{addressId}]")
        setAllDefaultFalse(userId)
        updateAddress({"id": addressId}, {"isDefault": True, "updatedAt": formatDateTime()})
        return returnResponse(2141)
    except Exception as e:
        logger.error(f"Error setting default address: {str(e)}")
        return returnResponse(2142)


@router.get("/user/addresses")
async def getUserAddresses(request: Request):
    try:
        userId = request.state.userMetadata.get("id")
        logger.info(f"Fetching addresses for user [{userId}]")
        result = getUserAddressesFromDb({"userId": userId})
        return returnResponse(2143, result=result)
    except Exception as e:
        logger.error(f"Error fetching addresses: {str(e)}")
        return returnResponse(2144)


@router.get("/user/addresses/{addressId}")
async def getAddress(addressId: str):
    try:
        logger.info(f"Fetching address by ID: {addressId}")
        addressData = getAddressById({"id": addressId})
        print(addressData)
        return returnResponse(2145, result=addressData)
    except Exception as e:
        logger.error(f"Error fetching address: {str(e)}")
        return returnResponse(2146)
