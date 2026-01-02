from sqlalchemy.orm import Session
from app.models.user import User
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.emailpassword.asyncio import get_user_by_id
from typing import Optional
import asyncio


async def _get_user_email_from_supertokens(user_id: str) -> str:
    """Get user email from SuperTokens"""
    try:
        user_info = await get_user_by_id(user_id)
        return user_info.email if user_info else ""
    except Exception as e:
        print(f"Error getting user email from SuperTokens: {e}")
        return ""


def get_or_create_user(db: Session, session: SessionContainer) -> User:
    """Get or create a user from SuperTokens session"""
    supertokens_user_id = session.get_user_id()
    
    # Try to get existing user
    user = db.query(User).filter(
        User.supertokens_user_id == supertokens_user_id
    ).first()
    
    if user:
        return user
    
    # Create new user - get email from SuperTokens
    try:
        # Get email from SuperTokens emailpassword recipe
        email = asyncio.run(_get_user_email_from_supertokens(supertokens_user_id))
        if not email:
            # Fallback: use user_id as email placeholder
            email = f"{supertokens_user_id}@supertokens.local"
    except Exception as e:
        print(f"Error getting user email: {e}")
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

