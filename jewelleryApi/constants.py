import os

# =========================
#  Keycloak Configuration
# =========================
keycloakUrl = os.getenv("KEYCLOAK_URL", "http://localhost:8080/auth")
keycloakAdmin = os.getenv("KEYCLOAK_ADMIN", "keycloakadmin")
keycloakAdminSecretKey = os.getenv("KEYCLOAK_ADMIN_SECRET_KEY", "keycloakadmin")
keycloakRealm = os.getenv("KEYCLOAK_REALM", "sso-realm")
keycloakClientId = os.getenv("KEYCLOAK_CLIENT_ID", "sso-client")
keycloakClientSecret = os.getenv("KEYCLOAK_CLIENT_SECRET_KEY", "RJfiAZfdwRAQB02XtAJoV4E186zMCULG")
keycloakBaseUrl = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
keycloakRedirectUri = os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:8000/auth/callback")
tokenUrl = os.getenv("TOKEN_URL", f"{keycloakBaseUrl}/realms/{keycloakRealm}/protocol/openid-connect/token")
authUrl = os.getenv("AUTH_URL", f"{keycloakBaseUrl}/realms/{keycloakRealm}/protocol/openid-connect/auth")

# ======================
#  MongoDB Configuration
# ======================
mongoUrl = os.getenv("MONGO_DB_URL", "mongodb://localhost:57057/")
mongoDatabase = os.getenv("MONGO_DATABASE_NAME", "SSOData")
mongoUserCollection = os.getenv("MONGO_USER_COLLECTION_NAME", "users")
mongoResetPasswordCollection = os.getenv("MONGO_RESET_PASSWORD_COLLECTION_NAME", "passwordReset")
mongoEmailVerifyCollection = os.getenv("MONGO_EMAILVERIFY_COLLECTION_NAME", "emailVerifyCollection")
mongoPhoneVerifyCollection = os.getenv("MONGO_PHONEVERIFY_COLLECTION_NAME", "phoneVerifyCollection")


# ======================
#  Frontend + Misc
# ======================
frontendUrl = os.getenv("FRONTEND_URL", "http://localhost:5173")
staticImagesPath = os.getenv("STATIC_IMAGES_PATH", "static/images")
isExchangeToken = os.getenv("IS_EXCHANGE_TOKEN", "false").lower() == "true"
