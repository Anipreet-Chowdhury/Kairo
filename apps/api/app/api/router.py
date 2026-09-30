from fastapi import APIRouter

from app.api.routes.courses import router as courses_router
from app.api.routes.health import router as health_router
from app.api.routes.membership import router as memberships_router
from app.api.routes.offerings import router as offerings_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(courses_router)
api_router.include_router(offerings_router)
api_router.include_router(memberships_router)
