from fastapi import APIRouter, Request
from Razor_pay.Models.planModel import PlanRequest
from Razor_pay.Services.razorpayClient import client
from ReturnLog.logReturn import returnResponse
from yensiAuthentication import logger
from Razor_pay.Database.plansDb import *

router = APIRouter(prefix="/subscriptions",tags=["Plan Service"])

@router.get("/plans")
def getSubscriptionPlans(request: Request):
    try:
        logger.info("Fetching all Razorpay plans.")
        plans = getAllPlans()
        logger.info("Plans fetched successfully.")
        return returnResponse(1510, result=plans)
    except Exception as e:
        logger.error("Failed to fetch Razorpay plans,Error: %s", str(e))
        return returnResponse(1511)


@router.post("/plan")
def createSubscriptionPlan(request:Request,payload: PlanRequest):
    try:
        # userRole = request.state.userMetadata.get("role")
        logger.info("Creating Razorpay plan.")
        plan = client.plan.create(payload.model_dump(exclude_unset=True))
        filteredPlan = {
            "planId": plan.get("id"),
            "period": plan.get("period"),
            "interval": plan.get("interval"),
            "item": {
                "name": plan["item"].get("name"),
                "amount": plan["item"].get("amount"),
                "currency": plan["item"].get("currency"),
                "description": plan["item"].get("description")
            },
            "notes": plan.get("notes", {})
        }
        insertPlan(filteredPlan)
        filteredPlan.pop("_id", None) 
        logger.info("Plan created successfully.")
        return returnResponse(1512, result=filteredPlan)
    except Exception as e:
        logger.error("Failed to create Razorpay plan,Error: %s", str(e))
        return returnResponse(1513)


@router.get("/plans/{planId}")
def fetchSubscriptionPlan(request:Request,planId: str):
    try:
        logger.info(f"Fetching Razorpay plan with ID: {planId}")
        plan = getPlanById(planId)
        return returnResponse(1514, result=plan)
    except Exception as e:
        logger.error(f"Failed to fetch Razorpay plan,Error: {str(e)}")
        return returnResponse(1515)