from fastapi import Request
from yensiAuthentication import logger



def hasRequiredRole(request: Request, requiredRoles: list):
    userMetadata = request.state.userMetadata  
    userRole = userMetadata.get("role")  
   
    if not userRole in requiredRoles:
        logger.warning('Unauthorized access attempt by user with roles: %s', userRole)
        return False
    return True