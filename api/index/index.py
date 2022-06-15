from fastapi import APIRouter

router = APIRouter(tags=['index'])


@router.get("/")
async def root():
    return {"message": "Hello World"}
