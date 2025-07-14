from fastapi import APIRouter, Request
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from Razor_pay.Database.tokensDb import *
from Razor_pay.Utils.util import getCustomerId
from Razor_pay.Utils.tokenUtils import adjustUserTokenBalance
from Razor_pay.Models.tokenModel import *
from yensiDatetime.yensiDatetime import formatDateTime
from yensiAuthentication.mongoData import updateUser

router = APIRouter(prefix="/tokens", tags=["Tokens Service"])


@router.get("/balance")
async def getTokenBalance(request: Request):
    try:
        logger.info("Token balance fetch request received")

        userId = request.state.userMetadata.get("id")
        if not userId:
            logger.warning("userId not found in request.state.userMetadata")
            return returnResponse(2014)

        logger.info(f"Resolved userId: {userId}")


        tokenData = getTokenBalanceByUserId(userId)

        now = formatDateTime()

        # Check and reset if cycle has ended
        cycleEnd = tokenData.get("cycleEnd")
        if cycleEnd and now >= cycleEnd:
            logger.info(f"Cycle ended for userId: {userId}. Resetting token fields.")
            tokenData["cycleEnd"] = "0"
            tokenData["cycleStart"] = "0"
            tokenData["totalAllocated"] = 0
            tokenData["currentTokens"] = 0

        logger.info(f"Token balance retrieved for userId: {userId}")

        return returnResponse(1586, result=tokenData)

    except Exception as e:
        logger.error(f"Exception while fetching token balance for userId: {userId if 'userId' in locals() else 'N/A'} - {str(e)}", exc_info=True)
        return returnResponse(1579)


@router.post("/adjust/{userId}")
async def adjustTokens(userId:str,payload: AdjustTokenRequest, request: Request):
    """
    Adjusts the user's token balance based on the type.

    - Subtracts tokens if type is 'consume'
    - Adds tokens if type is 'bonus' or 'refund'
    - Prevents balance from going below zero
    - Logs the token adjustment
    """
    try:
        logger.info("Token adjustment request received")

        logger.info(f"userId resolved: {userId}")
        logger.info(f"Adjustment type: {payload.type}, tokens: {payload.tokens}")

        updatedTokens = adjustUserTokenBalance(userId, payload)
        logger.info(f"Updated token balance calculated: {updatedTokens}")

        if updatedTokens < 0:
            logger.warning("Token adjustment would result in negative balance")
            return returnResponse(1581)

        now = formatDateTime()
        updateToken = {
            "currentTokens": updatedTokens,
            "lastUpdated": now
        }

        logger.info("Updating token balance in database")
        resultData = updateTokenBalance(userId, updateToken)
        if not resultData:
            logger.error("Failed to update token balance")
            return returnResponse(1582)

        updateUser(
            {"id": userId},
            {"userMetadata.paymentSubscription.subscriptionTokenBalance": updatedTokens}
        )
        logger.info("User document updated with new token balance")

        insertTokenLog({
            "userId": userId,
            "type": payload.type,
            "tokens": abs(payload.tokens),
            "reason": payload.reason,
            "meta": payload.meta or {},
            "timestamp": now
        })
        logger.info("Token transaction log inserted")

        logger.info("Token adjustment completed successfully")
        return returnResponse(1587, result=resultData)

    except Exception as e:
        logger.error(f"Error during token adjustment for userId={userId if 'userId' in locals() else 'unknown'}: {str(e)}", exc_info=True)
        return returnResponse(1580)


@router.post("/topup/{userId}")
async def topupTokens(request: Request,payload: TopUpRequest,userId:str):
    """
    Handles token topup  for a user.

    - Gets user ID from the request.
    - Uses `tokens` to update the token balance.
    - Adds `lastUpdated` timestamp and removes `tokens` before saving.
    - Logs the operation and updates user metadata.

    Parameters:
    - payload: TopUpRequest with tokens and optional details.
    - request: FastAPI request with user info.

    Returns:
    - JSON response with the result status.
    """
    try:
        logger.info("Token topup request received")

        logger.info(f"userId resolved: {userId}")
        logger.info(f"Topup type: topup, tokens: {payload.tokens}")

        now = formatDateTime()

        # Prepare clean payload (without 'tokens') and add lastUpdated
        cleanPayload = payload.model_dump(exclude={"tokens","reason","meta"}, exclude_none=True)
        cleanPayload["currentTokens"] = payload.tokens
        cleanPayload["totalAllocated"] = payload.tokens
        cleanPayload["lastUpdated"] = now

        resultData = updateTokenBalance(userId, cleanPayload)
        if not resultData:
            logger.error("Failed to update token balance during top-up")
            return returnResponse(1582)

        logger.info("Token balance updated in database")

        insertTokenLog({
            "userId": userId,
            "type": "topup",
            "tokens": abs(payload.tokens),
            "reason": payload.reason,
            "meta": payload.meta,
            "timestamp": now
        })
        logger.info("Token top-up log inserted")

        updateUser(
            {"id": userId},
            {"userMetadata.paymentSubscription.subscriptionTokenBalance": abs(payload.tokens)}
        )
        logger.info("User document updated with top-up balance")

        logger.info("Token top-up completed successfully")
        return returnResponse(1588, result=resultData)

    except Exception as e:
        logger.error(f"Error during token top-up : {str(e)}", exc_info=True)
        return returnResponse(1584)


@router.get("/history")
async def getTokenHistory(request: Request):
    try:
        logger.info("Token history request received")

        userId = request.state.userMetadata.get("id")
        logger.info(f"userId resolved: {userId}")

        cursor = getTokenHistoryFromTokenLog(userId, 50)
        logger.info("Token history fetched successfully")

        return returnResponse(1589, result=cursor)

    except Exception as e:
        logger.error(f"Error fetching token history for userId={userId if 'userId' in locals() else 'unknown'}: {str(e)}", exc_info=True)
        return returnResponse(1585)