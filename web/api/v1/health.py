from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()
@router.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy"
        }
    )
