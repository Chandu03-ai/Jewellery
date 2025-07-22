from Database.MongoData import shippingCollection


def createShipmentDb(shipment: dict):
    return shippingCollection.insert_one(shipment)


def getShipmentFromDb(query: str):
    return shippingCollection.find_one(query, {"_id": 0})

def getShipmentDb(awbNumber: str):
    return shippingCollection.find_one({"awbNumber": awbNumber}, {"_id": 0})


def updateShipmentStatusDb(awbNumber: str, status: str):
    return shippingCollection.update_one({"awbNumber": awbNumber}, {"$set": {"status": status}})
