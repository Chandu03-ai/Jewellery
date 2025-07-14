from pymongo import MongoClient
from constants import mongoUrl,mongoCustomersCollection,mongoDatabase,mongoOrdersCollection,mongoPaymentsCollection,mongoPlansCollection,mongoSubscriptionsCollection,mongoInvoiceCollection,mongoTokensCollection,mongoTokenLogCollection

client = MongoClient(mongoUrl)
db = client[mongoDatabase]
ordersCollection = db[mongoOrdersCollection]
paymentsCollection = db[mongoPaymentsCollection]   
customersCollection = db[mongoCustomersCollection]
plansCollection = db[mongoPlansCollection]
subscriptionCollection = db[mongoSubscriptionsCollection]
invoiceCollection = db[mongoInvoiceCollection]
tokensCollection = db[mongoTokensCollection]
tokenLogCollection = db[mongoTokenLogCollection]
