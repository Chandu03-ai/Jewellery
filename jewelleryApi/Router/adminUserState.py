from fastapi import APIRouter, Request
from yensiAuthentication.yensiConfig import logger
from yensiAuthentication.mongoData import getAllUsers, updateUser
from Models.userModel import UserRoles
from ReturnLog.logReturn import returnResponse
from Utils.utils import hasRequiredRole

router = APIRouter()


@router.get("/admin/users")
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


@router.put("/admin/users/{userId}/role")
async def updateUserRole(request: Request, userId: str, role: dict):
    try:
        requiredRoles = [UserRoles.Admin.value]
        if not hasRequiredRole(request, requiredRoles):
            logger.warning(f"Unauthorized role update attempt by user [{request.state.userMetadata.get('id')}]")
            return returnResponse(2000)

        query = {"id": userId}
        result = updateUser(query, role)
        if result.modified_count == 1:
            logger.info(f"Role for user [{userId}] set to [{role}]")
            return returnResponse(2122)
        else:
            logger.warning(f"No user updated. User [{userId}] not found or already has role [{role}].")
            return returnResponse(2123)

    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}", exc_info=True)
        return returnResponse(2124)
