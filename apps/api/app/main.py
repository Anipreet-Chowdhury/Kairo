from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="Kairo API",
    description="BackendAPI for Kairo application",
    version="0.1.0",
)

app.include_router(api_router)
