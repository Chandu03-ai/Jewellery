from Razor_pay.Database.db import customersCollection


def insertCustomerData(customer):
    """
    Insert a new customer into the customers collection.
    """
    return customersCollection.insert_one(customer)

def getCustomerById(customerId):
    """
    Retrieve a customer by their ID.
    """
    customer = customersCollection.find_one({"customerId": customerId})
    if customer and "_id" in customer:
        customer["_id"] = str(customer["_id"])  # Serialize ObjectId    
    return customer

def getAllCustomers():
    """
    Retrieve all customers and return as a dictionary with customerId as the key.
    """
    customers = list(customersCollection.find({}))
    for customer in customers:
        customer_id = customer.get("customerId")
        if customer_id:
            customer["_id"] = str(customer["_id"])  # Serialize ObjectId
    return customers

def updateCustomerData(customerId, updatedCustomer):
    """
    Update an existing customer by their ID.
    """
    result = customersCollection.update_one({"customerId": customerId}, {"$set": updatedCustomer})
    if result.matched_count > 0:
        return True
    return False