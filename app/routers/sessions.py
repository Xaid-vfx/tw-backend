

from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/create-session")
async def create_session(
    current_user: User = Depends(get_current_user)
):
    pass