from Razor_pay.Database.db import paymentsCollection

def insertPaymentData(paymentData: dict):
    try:
        data = paymentsCollection.insert_one(paymentData)
        paymentData.pop("_id", None)  
        return data  # Return the inserted data
    except Exception as e:
        raise Exception(f"Failed to insert payment data: {e}")

def getPaymentById(paymentId: str):
    try:
        data = paymentsCollection.find_one({"paymentId": paymentId})
        if data:
            data.pop("_id", None)  
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch payment by ID: {e}")

def updatePayment(paymentId: str, updateData: dict):
    try:
        result = paymentsCollection.update_one({
            "paymentId": paymentId
        }, {
            "$set": updateData
        })  
        return result.modified_count
    except Exception as e:
        raise Exception(f"Failed to update payment: {e}")

def listPayments(query: dict = {}):
    try:
        data = list(paymentsCollection.find(query))
        for item in data:
            item.pop("_id", None)  
        return data
    except Exception as e:
        raise Exception(f"Failed to list payments: {e}")

def upsertPayment(paymentId: str, paymentData: dict):
    try:
        result = paymentsCollection.update_one(
            {"paymentId": paymentId},
            {"$set": paymentData},
            upsert=True
        )
        return {
            "status": "inserted" if result.upserted_id else "updated",
            "paymentId": paymentId
        }
    except Exception as e:
        raise Exception(f"Failed to upsert payment: {e}")