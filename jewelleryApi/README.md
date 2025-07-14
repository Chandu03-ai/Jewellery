# 🚀 jewelleryApi

## 📦 Project Setup

## **Step 1: Create a Virtual Environment**  

Before installing dependencies, create and activate a virtual environment:  

### **For Windows (PowerShell):**  

 powershell
python -m venv venv-jewelleryapi

venv-jewelleryapi\Scripts\Activate



> Ensure the virtual environment is activated before proceeding to install dependencies.  

---

## **Step 2: Install Required Python Packages**  

For local development, install the required dependencies:  


 bash
pip install -r requirements.txt --index-url https://pypi.org/simple --extra-index-url http://192.168.0.104:8081/repository/packageREPO/simple/ --trusted-host 192.168.0.104



---

## **Step 3: Add a .env File**

Create a .env file in the root directory with the following content:

<details>
<summary>Click to view full <code>.env</code> content</summary>


 env
# -------- Keycloak Configuration --------
KEYCLOAK_URL=http://localhost:8080/auth
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REDIRECT_URI=http://localhost:8000/auth/callback
TOKEN_URL=http://localhost:8080/realms/sso-realm/protocol/openid-connect/token
AUTH_URL=http://localhost:8080/realms/sso-realm/protocol/openid-connect/auth

KEYCLOAK_ADMIN=keycloakadmin
KEYCLOAK_ADMIN_SECRET_KEY=keycloakadmin
KEYCLOAK_REALM=sso-realm
KEYCLOAK_CLIENT_ID=sso-client
KEYCLOAK_CLIENT_SECRET_KEY=RJfiAZfdwRAQB02XtAJoV4E186zMCULG
IS_EXCHANGE_TOKEN=false

# -------- Frontend Configuration --------
FRONTEND_URL=http://localhost:5173

# -------- MongoDB Configuration --------
MONGO_DB_URL=mongodb://admin:admin@localhost:57057/jewelleryApi?authSource=admin
MONGO_DATABASE_NAME=jewelleryApi
MONGO_USER_COLLECTION_NAME=users
MONGO_RESET_PASSWORD_COLLECTION_NAME=passwordReset

# -------- Miscellaneous --------
STATIC_IMAGES_PATH=static/images



</details>

---

## **Step 4: Run Docker Compose**

Start **Keycloak, PostgreSQL, and MongoDB** services using:


 bash
docker compose -f jewelleryapi-docker-compose.yml up -d



> This will start the containers in detached mode.

---

## **Step 5: Run Uvicorn**


 powershell
uvicorn main:app --reload



---
