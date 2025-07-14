from Razor_pay.Database.db import plansCollection

def insertPlan(plan):
    """
    Insert a new plan into the plans collection.
    """
    result = plansCollection.insert_one(plan)
    return str(result.inserted_id)  

def getPlanById(planId):
    """
    Retrieve a plan by its ID, excluding _id.
    """
    return plansCollection.find_one({"planId": planId}, {"_id": 0})

def getAllPlans():
    """
    Retrieve all plans and return as a dictionary with planId as the key, excluding _id.
    """
    plans = {}
    for plan in plansCollection.find({}, {"_id": 0}):  # 👈 exclude _id here
        plan_id = plan.get("planId")
        if plan_id:
            plans[plan_id] = plan
    return plans
