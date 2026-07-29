import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from api.dependencies.services import get_auth_service
from application.auth.service import AuthService
from domain.user.models import TokenResponse, UserCreate, UserLogin, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])
security = HTTPBearer(auto_error=False)


@router.post("/auth/signup", response_model=TokenResponse)
async def signup(
    data: UserCreate,
    auth: AuthService = Depends(get_auth_service),
):
    try:
        return await auth.register(data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    auth: AuthService = Depends(get_auth_service),
):
    try:
        return await auth.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/auth/me", response_model=UserResponse)
async def get_me(
    user=Depends(security),
    auth: AuthService = Depends(get_auth_service),
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = AuthService.verify_token(user.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = await auth.get_user_by_id(user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=u.id, email=u.email, full_name=u.full_name, created_at=u.created_at
    )
