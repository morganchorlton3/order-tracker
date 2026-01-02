from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class OAuthState(Base):
    """Temporary storage for OAuth state and PKCE code_verifier"""
    __tablename__ = "oauth_states"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, unique=True, index=True, nullable=False)
    code_verifier = Column(String, nullable=False)
    source = Column(String, nullable=False, default="etsy")  # "etsy" or "tiktok_shop"
    created_at = Column(DateTime, server_default=func.now())

