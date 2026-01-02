from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.core.auth import supertokens_middleware
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Order Tracker API",
    description="API for managing orders and products from Etsy and TikTok Shop",
    version="1.0.0",
)

# SuperTokens middleware (must be added before CORS)
# This middleware handles all /auth/* routes automatically
app.add_middleware(supertokens_middleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Order Tracker API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

