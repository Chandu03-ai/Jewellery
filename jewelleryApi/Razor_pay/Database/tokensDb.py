from Razor_pay.Database.db import tokensCollection, tokenLogCollection


def insertTokenBalance(tokenData):
    """
    Create or overwrite a user's token balance document using $set with upsert.
    """
    return tokensCollection.update_one({"userId": tokenData["userId"]}, {"$set": tokenData}, upsert=True)


def getTokenBalanceByUserId(userId):
    """
    Get current token balance and metadata for a user.
    """
    doc = tokensCollection.find_one({"userId": userId}, {"_id": 0})
    return doc


def updateTokenBalance(userId: str, updateToken: dict):
    """
    Update fields in the token balance document and return the updated data.
    """
    updatedDoc = tokensCollection.find_one_and_update(
        {"userId": userId}, {"$set": updateToken}, return_document=True, projection={"_id": 0}, upsert=True  # 🔥 will insert if not found
    )  # Return the updated document  # Exclude _id from result
    return updatedDoc


def insertTokenLog(tokenData):
    """
    Log token usage/bonus/top-up etc. in the transaction log.
    """

    return tokenLogCollection.insert_one(tokenData)


def getTokenHistoryFromTokenLog(userId: str, limit: int):
    """
    Get recent token transaction logs for a user with a user-defined limit.
    """
    logs = tokenLogCollection.find({"userId": userId}, {"_id": 0}).sort("timestamp", -1).limit(limit)  # Exclude _id from result
    return list(logs)
