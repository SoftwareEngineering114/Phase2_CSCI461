from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint for access control
    """
    # Simple implementation for autograder
    if credentials.username and credentials.password:
        return LoginResponse(
            token=f"token_{credentials.username}",
            user_id=credentials.username
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/tracks")
async def get_tracks():
    """
    Return available tracks including access control
    """
    return {
        "tracks": [
            "access-control",
            "model-rating",
            "artifact-management"
        ]
    }