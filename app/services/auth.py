from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from typing import Optional
from bcrypt import hashpw, gensalt, checkpw
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

security = HTTPBasic()

# Get admin hash from environment variable
USERS = {
    "admin": os.getenv("ADMIN_HASH", "").encode()
}

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    stored_hash = USERS[credentials.username]
    if not checkpw(credentials.password.encode(), stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username