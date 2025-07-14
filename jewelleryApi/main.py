from fastapi import FastAPI
from yensiAuthentication import logger,yensiloginRouter,yensiSsoRouter
from Router import generalRouter
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
app.include_router(generalRouter.router)

# run the FastAPI application
if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
