from fastapi import APIRouter, Request
from pymongo import MongoClient
import requests
from constants import mongoUrl, keycloakBaseUrl, keycloakRealm, keycloakClientId, keycloakClientSecret
from yensiAuthentication.yensiConfig import logger
from yensiAuthentication.mongoData import getAllUsers
from Models.userModel import UserRoles
from ReturnLog.logReturn import returnResponse
from Utils.utils import hasRequiredRole

router = APIRouter()

mongoClient = MongoClient(mongoUrl)


@router.get("/health")
async def healthCheck():
    """
    Health check endpoint to verify MongoDB and Keycloak connectivity.
    """
    health_status = {"status": "OK", "mongodb": "Unknown", "keycloak": "Unknown"}

    try:
        logger.debug("Starting health check process.")

        # MongoDB Health Check
        try:
            mongoClient = MongoClient(mongoUrl, serverSelectionTimeoutMS=3000)
            mongoClient.admin.command("ping")
            health_status["mongodb"] = "Connected"
            logger.info("MongoDB is reachable.")
        except Exception as e:
            health_status["mongodb"] = "Not Connected"
            logger.error(f"MongoDB connection failed: {str(e)}")

        # Keycloak Client Verification
        try:
            tokenEndpoint = f"{keycloakBaseUrl}/realms/{keycloakRealm}/protocol/openid-connect/token"
            payload = {"client_id": keycloakClientId, "client_secret": keycloakClientSecret, "grant_type": "client_credentials"}
            response = requests.post(tokenEndpoint, data=payload, timeout=3)

            if response.status_code == 200:
                health_status["keycloak"] = "Authenticated"
                logger.info("Keycloak authentication successful.")
            else:
                raise Exception(f"Response: {response.status_code}, {response.text}")

        except Exception as e:
            health_status["keycloak"] = "Not Authenticated"
            logger.error(f"Keycloak authentication failed: {str(e)}")

        # Overall Status
        if "Not Connected" in health_status.values() or "Not Authenticated" in health_status.values():
            health_status["status"] = "Degraded"

        logger.info(f"Health check result: {health_status}")
        return health_status

    except Exception as e:
        logger.critical(f"Unexpected health check failure: {str(e)}", exc_info=True)
        return {"status": "Critical", "mongodb": "Unknown", "keycloak": "Unknown"}


@router.get("/users")
async def getAllUser(request: Request):
    try:
        requiredRoles = [UserRoles.Admin.value]
        if not hasRequiredRole(request, requiredRoles):
            logger.warning("unAuthorized access attempt ")
            return returnResponse(2000)

        logger.info("Fetching all users.")
        users = list(getAllUsers({}))
        if not users:
            logger.warning("No users found.")
            return returnResponse(2111)

        result = [{**{key: value for key, value in doc.items() if key not in ("_id", "keycloakId")}} for doc in users]
        logger.info(f"users retrieved successfully")
        return returnResponse(2110, result)
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}", exc_info=True)
        return returnResponse(2112)
