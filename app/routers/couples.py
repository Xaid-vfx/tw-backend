from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/couples", tags=["couples"])

@router.post("")
async def create_couple():
    # TODO: Implement couple creation logic
    return JSONResponse({"id": 1, "members": ["user1@example.com", "user2@example.com"]})

@router.get("/{couple_id}")
async def get_couple(couple_id: int):
    # TODO: Implement couple info retrieval logic
    return JSONResponse({"id": couple_id, "members": ["user1@example.com", "user2@example.com"]}) 