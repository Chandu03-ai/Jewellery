from fastapi import APIRouter, Request
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from Razor_pay.Database.tokensDb import *
from Razor_pay.Utils.util import getCustomerId
from Razor_pay.Utils.tokenUtils import adjustUserTokenBalance
from Razor_pay.Models.tokenModel import *
from yensiDatetime.yensiDatetime import formatDateTime
from yensiAuthentication.mongoData import updateUser

router = APIRouter(prefix="/team", tags=["Tokens Service"])


@router.post("/addMember")
async def addToTeam(request: Request):
    try:
        logger.debug("addToTeam started")
        # Business logic here
        result = None
        return returnResponse(200, result=result)
    except Exception as e:
        logger.error("addToTeam error: %s", str(e))
        return returnResponse(500)
    

@router.get("/getMembers")
async def getMembersFromTeam(request: Request):
    try:
        logger.debug("getMembersFromTeam started")
        # Business logic here
        result = None
        return returnResponse(200, result=result)
    except Exception as e:
        logger.error("getMembersFromTeam error: %s", str(e))
        return returnResponse(500)
  
