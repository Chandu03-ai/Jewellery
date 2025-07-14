from yensiDatetime.yensiDatetime import formatDateTime
from Razor_pay.Database.tokensDb import getTokenBalanceByUserId, insertTokenBalance, insertTokenLog
from yensiAuthentication import logger
from yensiAuthentication.mongoData import updateUser
from Razor_pay.Database.plansDb import getPlanById
from Razor_pay.Utils.util import convertEpochToCycleData

def allocateTokensOnSubscription(subscriptionData: dict):
    """
    Allocates tokens to a user when their subscription starts.

    - Gets token count from the plan.
    - Calculates cycle start and end times.
    - Saves token balance to DB.
    - Updates user token info and logs the allocation.
    """
    try:
        logger.info(f"Starting allocation for userId: {subscriptionData.get('userId')}, subscriptionId: {subscriptionData.get('subscriptionId')}")
        now = formatDateTime()
        plan = getPlanById(subscriptionData["planId"])
        tokensAllocated = int(plan.get("notes", {}).get("tokens", 0))
        period = plan.get("period")
        interval = plan.get("interval")
        cycleData = convertEpochToCycleData(subscriptionData.get("subscriptionStartTime"), period,interval)
        cycleStart = cycleData["givenTime"]
        cycleEnd = cycleData["periodEnd"]

        logger.debug(f"Formatted current timestamp: {now}")
        logger.debug(f"Tokens to allocate: {tokensAllocated}")

        tokenPayload = {
            "userId": subscriptionData["userId"],
            "planId": subscriptionData["planId"],
            "subscriptionId": subscriptionData["subscriptionId"],
            "currentTokens": tokensAllocated,
            "totalAllocated": tokensAllocated,
            "cycleStart": cycleStart,
            "cycleEnd": cycleEnd if cycleEnd not in [None, ""] else subscriptionData["subscriptionEndTime"],
            "lastUpdated": now,
        }

        logger.debug(f"Prepared tokenPayload: {tokenPayload}")

        # Insert into balance collection
        insertTokenBalance(tokenPayload)
        logger.info(f"Token balance inserted for userId: {subscriptionData['userId']}")

        # Update user with new balance
        updateUser({"id": subscriptionData["userId"]}, {"userMetadata.paymentSubscription.subscriptionTokenBalance": tokensAllocated})
        logger.info(f"User document updated with token balance for userId: {subscriptionData['userId']}")

        # Insert into token transaction log
        tokenLogPayload = {
            "userId": subscriptionData["userId"],
            "type": "topup",
            "tokens": abs(tokensAllocated),
            "reason": "Initial subscription allocation",
            "meta": subscriptionData.get("meta") or {},
            "timestamp": now,
        }

        logger.debug(f"Prepared tokenLog payload: {tokenLogPayload}")

        insertTokenLog(tokenLogPayload)
        logger.info(f"Token transaction log inserted for userId: {subscriptionData['userId']}")

        logger.info(f"Successfully allocated {tokensAllocated} tokens to userId: {subscriptionData['userId']} for subscriptionId: {subscriptionData['subscriptionId']}")

    except Exception as e:
        logger.error(f"Error during token allocation: {str(e)}", exc_info=True)


def adjustUserTokenBalance(userId: str, payload: dict = {}):
    """
    Adjusts the token balance for a user and logs the change.

    Args:
        userId (str): User ID
        tokenChange (int): Positive number of tokens (logic for +/- handled here)
        changeType (str): Type of change ('consume', 'bonus', etc.)
        reason (str): Description of the reason
        meta (dict): Optional metadata

    Returns:
        dict: Updated token balance or error info
    """
    try:
        logger.info("Fetching current token balance")

        tokenData = getTokenBalanceByUserId(userId)
        currentTokens = tokenData.get("currentTokens", 0)

        logger.info("Calculating token change based on adjustment type")
        tokenChange = payload.tokens
        if payload.type == "consume":
            tokenChange = -abs(payload.tokens)
            logger.info("Token type is 'consume'; tokens will be deducted")
        elif payload.type in ["bonus", "refund"]:
            tokenChange = abs(payload.tokens)
            logger.info(f"Token type is '{payload.type}'; tokens will be added")
        else:
            logger.warning("Unsupported token type received")
            raise ValueError("Unsupported token type")

        updatedTokens = currentTokens + tokenChange
        return updatedTokens

    except Exception as e:
        logger.error(f"Token adjustment failed: {str(e)}", exc_info=True)
        return {"error": "Internal error during token adjustment"}
