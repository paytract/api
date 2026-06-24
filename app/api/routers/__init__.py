from fastapi import APIRouter

from . import auth, profile

routes = APIRouter(prefix="/api/v1")

routes.include_router(auth.router)
routes.include_router(profile.router)
