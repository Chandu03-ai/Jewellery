from fastapi import FastAPI
from yensiAuthentication import logger,yensiloginRouter,yensiSsoRouter
from Router import generalRouter,productRouter,categoryRouter,cartRouter,reviewRouter,tagRouter,variantRouter,utilityRouter
from Razor_pay.Routers import customerService,orderService,paymentService,webhookService
from fastapi.middleware.cors import CORSMiddleware
from yensiAuthentication.authenticate import KeycloakMiddleware
import uvicorn

# Start the FastAPI application
logger.info("FastAPI application starting...")


# Create FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Keycloak middleware for authentication
app.add_middleware(KeycloakMiddleware)

# Include authentication router
app.include_router(yensiloginRouter)
app.include_router(yensiSsoRouter)
app.include_router(customerService.router)
app.include_router(orderService.router)
app.include_router(paymentService.router)
app.include_router(webhookService.router)
app.include_router(generalRouter.router)
app.include_router(productRouter.router)
app.include_router(categoryRouter.router)
app.include_router(cartRouter.router)
app.include_router(tagRouter.router)
app.include_router(variantRouter.router)
app.include_router(reviewRouter.router)
app.include_router(utilityRouter.router)



# run the FastAPI application
if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
