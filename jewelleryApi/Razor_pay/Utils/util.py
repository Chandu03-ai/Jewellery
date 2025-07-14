from fastapi import Request
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from yensiAuthentication import logger


def cleanMongoId(doc: dict) -> dict:
    """
    Convert ObjectId to string for _id field in a MongoDB document.
    """
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def getCustomerId(request: Request):
    customerId = request.state.userMetadata.get("userMetadata", {}).get("paymentSubscription", {}).get("customerId")
    return customerId


def convertEpochToCycleData(epochTime, period: str = None, interval: int = None) -> dict:
    """
    Convert epoch timestamp or formatted datetime to a consistent string format.

    Parameters:
    - epochTime: int, float, or str ('YYYYMMDDHHmmssfff' or epoch)
    - period (optional): 'weekly', 'monthly', or 'yearly'

    Returns:
    {
        "givenTime": str,
        "periodEnd": str or None
    }
    """

    def format_datetime(dt: datetime) -> str:
        return dt.strftime("%Y%m%d%H%M%S") + f"{dt.microsecond // 1000:03d}"

    try:
        epochTimeStr = str(epochTime).strip()
        logger.info(f"[convertEpochToCycleData] Input time: {epochTimeStr}")

        # Already formatted datetime string (YYYYMMDDHHmmssfff)
        if len(epochTimeStr) == 17 and epochTimeStr.isdigit():
            baseTime = datetime.strptime(epochTimeStr, "%Y%m%d%H%M%S%f")
            givenTime = epochTimeStr
            logger.info("Detected formatted time input.")
        else:
            # Convert epoch to datetime
            ts = float(epochTimeStr)
            if ts > 1e12:
                ts /= 1000  # Handle milliseconds
            baseTime = datetime.fromtimestamp(ts, tz=timezone.utc)
            givenTime = format_datetime(baseTime)
            logger.info("Parsed epoch time to datetime.")

        result = {"givenTime": givenTime, "periodEnd": None}

        if period:
            i = interval or 1  # Default to 1 if interval is None

            if period == "daily":
                endTime = baseTime + timedelta(days=i)
            elif period == "weekly":
                endTime = baseTime + timedelta(weeks=i)
            elif period == "monthly":
                endTime = baseTime + relativedelta(months=i)
            elif period == "quarterly":
                endTime = baseTime + relativedelta(months=3 * i)
            elif period == "yearly":
                endTime = baseTime + relativedelta(years=i)
            else:
                logger.warning(f"Unknown period '{period}', cannot calculate periodEnd.")
                endTime = None

            if endTime:
                result["periodEnd"] = format_datetime(endTime)
                logger.info(f"Period '{period}' with interval {i} applied. periodEnd: {result['periodEnd']}")

        return result

    except Exception as e:
        logger.error(f"Failed to convert epochTime '{epochTime}': {str(e)}", exc_info=True)
        return {"givenTime": None, "periodEnd": None}
