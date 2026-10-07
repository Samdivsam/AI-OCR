from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.financial import router as financial_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(financial_router)

