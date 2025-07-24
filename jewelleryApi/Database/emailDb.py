from Database.MongoData import emailVerifyCollection

def insertData(query):
    return emailVerifyCollection.insert_one(query)