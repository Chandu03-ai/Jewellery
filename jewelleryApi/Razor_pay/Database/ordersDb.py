from Razor_pay.Database.db import ordersCollection


def insertOrder(order):
    """
    Insert a new order into the orders collection.
    """
    result = ordersCollection.insert_one(order)
    return str(result.inserted_id)

def getOrderById(orderId):
    """
    Retrieve an order by its ID.
    """
    order = ordersCollection.find_one({"orderId": orderId})
    if order and "_id" in order:
        order["_id"] = str(order["_id"])
    return order

def getAllOrders(query:dict = {}):
    """
    Retrieve all orders and return as a dictionary with orderId as the key.
    """
    orders = {}
    for order in ordersCollection.find(query):
        order_id = order.get("orderId")
        if order_id:
            order["_id"] = str(order["_id"]) 
            orders[order_id] = order
    return orders


def updateOrder(orderId, updatedOrder):
    """
    Update an existing order by its ID.
    """
    result = ordersCollection.update_one({"orderId": orderId}, {"$set": updatedOrder})
    if result.matched_count > 0:
        return True
    return False