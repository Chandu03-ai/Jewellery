from StatusCodes.statusCodes import CUSTOM_STATUS_CODES
from fastapi import Request
from yensiAuthentication import logger


def returnResponse(code, result=None):
    try:
        if not isinstance(code, int):
            raise TypeError("Code must be an integer")
        response = {"code": code, "message": CUSTOM_STATUS_CODES[code]["message"]}
        if result is not None:
            response["result"] = result
        return response

    except Exception as e:
        logger.error(f"Error creating a returnResponse : {str(e)}")
        raise e