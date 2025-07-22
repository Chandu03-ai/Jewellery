from Database.MongoData import addressesCollection


def insertAddress(address: dict):
    return addressesCollection.insert_one(address)


def updateAddress(query: dict, updateData: dict):
    return addressesCollection.update_one(query, {"$set": updateData})


def deleteAddress(query: dict):
    return addressesCollection.delete_one(query)


def getUserAddressesFromDb(query: dict):
    return list(addressesCollection.find(query, {"_id": 0}))


def getAddressById(query: dict):
    return addressesCollection.find_one(query, {"_id": 0})


def setAllDefaultFalse(userId: str):
    addressesCollection.update_many({"userId": userId}, {"$set": {"isDefault": False}})
