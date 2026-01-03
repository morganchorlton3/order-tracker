from sqlalchemy.orm import Session
from app.models.user import User
from supertokens_python.recipe.session import SessionContainer
from typing import Optional
import httpx
from app.core.config import settings


def _get_user_email_from_supertokens(user_id: str) -> Optional[str]:
    """Get user email from SuperTokens by making direct API call to core"""
    try:
        # Make direct HTTP request to SuperTokens core API
        connection_uri = settings.SUPERTOKENS_CONNECTION_URI.rstrip('/')
        url = f"{connection_uri}/recipe/user"
        
        headers = {}
        if settings.SUPERTOKENS_API_KEY:
            headers["api-key"] = settings.SUPERTOKENS_API_KEY
        
        response = httpx.get(
            url,
            params={"userId": user_id, "recipeId": "emailpassword"},
            headers=headers,
            timeout=5.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                user_data = data.get("user", {})
                # Email is typically in user.emails[0] or user.email
                if "emails" in user_data and user_data["emails"]:
                    return user_data["emails"][0]
                elif "email" in user_data:
                    return user_data["email"]
    except Exception as e:
        print(f"Error getting user email from SuperTokens: {e}")
        import traceback
        traceback.print_exc()
    
    return None


def get_or_create_user(db: Session, session: SessionContainer) -> User:
    """Get or create a user from SuperTokens session"""
    supertokens_user_id = session.get_user_id()
    
    # Try to get existing user
    user = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()
    
    # Get email from SuperTokens (always try to get fresh email)
    email = _get_user_email_from_supertokens(supertokens_user_id)
    
    # If user exists but has placeholder email, update it
    if user:
        if email and user.email.endswith('@supertokens.local'):
            user.email = email
            db.commit()
            db.refresh(user)
        return user
    
    # Create new user
    # Fallback if email couldn't be retrieved
    if not email:
        print(f"Warning: Could not retrieve email for user {supertokens_user_id}, using placeholder")
        email = f"{supertokens_user_id}@supertokens.local"
    
    user = User(
        supertokens_user_id=supertokens_user_id,
        email=email
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def get_current_user_id(db: Session, session: SessionContainer) -> Optional[int]:
    """Get the current user's database ID"""
    user = get_or_create_user(db, session)
    return user.id

