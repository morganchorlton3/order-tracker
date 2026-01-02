from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import settings
from app.models.oauth_token import OAuthToken
from app.models.oauth_state import OAuthState
import httpx
import secrets
import base64
import hashlib

router = APIRouter()


@router.get("/etsy/authorize")
async def etsy_authorize(db: Session = Depends(get_db)):
    """Initiate Etsy OAuth flow with PKCE"""
    if not settings.ETSY_API_KEY:
        raise HTTPException(status_code=400, detail="Etsy API key not configured")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Generate PKCE code verifier and challenge
    # Code verifier: a random string between 43-128 characters
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Code challenge: SHA256 hash of the code verifier, base64url encoded
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    # Store state and code_verifier in database for retrieval during callback
    oauth_state = OAuthState(
        state=state,
        code_verifier=code_verifier,
        source="etsy"
    )
    db.add(oauth_state)
    db.commit()
    
    auth_url = (
        f"https://www.etsy.com/oauth/connect?"
        f"response_type=code&"
        f"redirect_uri={settings.ETSY_REDIRECT_URI}&"
        f"scope=shops_r%20transactions_r%20listings_r%20listings_w&"
        f"client_id={settings.ETSY_API_KEY}&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )
    
    return {
        "authorization_url": auth_url,
        "state": state,
        "message": "Visit the authorization_url to authorize the application. After authorization, you'll be redirected back automatically."
    }


@router.get("/etsy/callback")
async def etsy_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Handle Etsy OAuth callback with PKCE"""
    if not settings.ETSY_API_KEY or not settings.ETSY_API_SECRET:
        raise HTTPException(status_code=400, detail="Etsy API credentials not configured")
    
    # Check if there was an error from Etsy
    if error:
        error_msg = f"OAuth error: {error}"
        if error_description:
            error_msg += f" - {error_description}"
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check if code is present
    if not code:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing authorization code. Please make sure you're accessing this URL "
                "as a redirect from Etsy's authorization page. Start the OAuth flow by "
                "visiting /api/v1/auth/etsy/authorize first."
            )
        )
    
    # Check if state is present
    if not state:
        raise HTTPException(
            status_code=400,
            detail="Missing state parameter. This is required for security."
        )
    
    # Retrieve code_verifier from database using state
    oauth_state = db.query(OAuthState).filter(
        OAuthState.state == state,
        OAuthState.source == "etsy"
    ).first()
    
    if not oauth_state:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid or expired state. Please start the OAuth flow again by "
                "visiting /api/v1/auth/etsy/authorize"
            )
        )
    
    code_verifier = oauth_state.code_verifier
    
    try:
        # Exchange authorization code for access token with PKCE
        # Etsy requires Basic Auth with keystring (API key) as username and shared secret as password
        token_url = "https://api.etsy.com/v3/public/oauth/token"
        
        api_key_preview = settings.ETSY_API_KEY[:8] + "..." if settings.ETSY_API_KEY and len(settings.ETSY_API_KEY) > 8 else settings.ETSY_API_KEY
        secret_preview = settings.ETSY_API_SECRET[:4] + "..." if settings.ETSY_API_SECRET and len(settings.ETSY_API_SECRET) > 4 else settings.ETSY_API_SECRET
        # Try different Basic Auth formats - Etsy documentation is unclear
        # Format 1: Combined 'keystring:shared_secret' as username
        combined_key = f"{settings.ETSY_API_KEY}:{settings.ETSY_API_SECRET}"
        combined_key_preview = combined_key[:20] + "..." if len(combined_key) > 20 else combined_key
        shop_info = {}

        async with httpx.AsyncClient() as client:
            # Try format: username = keystring, password = shared_secret (standard OAuth)
            response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.ETSY_API_KEY,
                    "code": code,
                    "redirect_uri": settings.ETSY_REDIRECT_URI,
                    "code_verifier": code_verifier,  # PKCE requirement
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=30.0
            )
            response.raise_for_status()
            token_data = response.json()
        
        # Etsy returns access_token in the response
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail=f"Etsy did not return an access token. Response: {token_data}"
            )

        shop_info = await _get_shop_info(token_data.get("access_token"))
        if not shop_info:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get shop info from Etsy API"
            )
        
        # Calculate expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store or update token in database
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.source == "etsy"
        ).first()

        print(f"Shop info: {shop_info}")
        
        if existing_token:
            existing_token.access_token = access_token
            existing_token.refresh_token = token_data.get("refresh_token")
            existing_token.token_type = token_data.get("token_type", "Bearer")
            existing_token.expires_at = expires_at
            existing_token.shop_id = shop_info.get("id", "")
            existing_token.shop_name = shop_info.get("name", "")
        else:
            new_token = OAuthToken(
                source="etsy",
                access_token=access_token,
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                expires_at=expires_at,
                shop_id=shop_info.get("id", ""),
                shop_name=shop_info.get("name", ""),
            )
            db.add(new_token)
        
        db.commit()
        
        # Clean up the temporary state record
        db.delete(oauth_state)
        db.commit()
        
        # Return HTML page that closes the popup and notifies parent
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Etsy Authentication</title>
        </head>
        <body>
            <h1>Authentication Successful!</h1>
            <p>Connected to {shop_info.get("name", "your Etsy shop")}</p>
            <p>You can close this window.</p>
            <script>
                // Notify parent window
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'ETSY_AUTH_SUCCESS',
                        shop_name: '{shop_info.get("name", "")}'
                    }}, window.location.origin);
                    // Close the popup
                    window.close();
                }} else {{
                    // If not in popup, redirect to sync page
                    setTimeout(function() {{
                        window.location.href = '/sync';
                    }}, 2000);
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_json = e.response.json()
            error_detail = str(error_json)
        except:
            pass
        
        # Provide detailed debugging information
        api_key_preview = settings.ETSY_API_KEY[:8] + "..." if settings.ETSY_API_KEY and len(settings.ETSY_API_KEY) > 8 else settings.ETSY_API_KEY
        secret_preview = settings.ETSY_API_SECRET[:4] + "..." if settings.ETSY_API_SECRET and len(settings.ETSY_API_SECRET) > 4 else settings.ETSY_API_SECRET
        combined_key = f"{settings.ETSY_API_KEY}:{settings.ETSY_API_SECRET}"
        combined_key_preview = combined_key[:30] + "..." if len(combined_key) > 30 else combined_key
        
        debug_info = (
            f"Status: {e.response.status_code}\n"
            f"Error: {error_detail}\n"
            f"Redirect URI used: {settings.ETSY_REDIRECT_URI}\n"
            f"Has API Key: {bool(settings.ETSY_API_KEY)}\n"
            f"Has API Secret: {bool(settings.ETSY_API_SECRET)}\n"
            f"API Key length: {len(settings.ETSY_API_KEY) if settings.ETSY_API_KEY else 0}\n"
            f"API Key preview: {api_key_preview}\n"
            f"Secret length: {len(settings.ETSY_API_SECRET) if settings.ETSY_API_SECRET else 0}\n"
            f"Secret preview: {secret_preview}\n"
            f"Combined key length: {len(combined_key)}\n"
            f"Combined key preview: {combined_key_preview}\n"
            f"Combined key format check: {'keystring:shared_secret' in combined_key if combined_key else 'N/A'}"
        )
        
        raise HTTPException(
            status_code=e.response.status_code,
            detail=(
                f"Failed to exchange authorization code: {error_detail}\n\n"
                f"Debug info:\n{debug_info}\n\n"
                f"Please verify:\n"
                f"1. ETSY_API_KEY is your keystring (not the app name)\n"
                f"2. ETSY_API_SECRET is your shared secret\n"
                f"3. Redirect URI in Etsy app settings matches exactly: {settings.ETSY_REDIRECT_URI}\n"
                f"4. The redirect URI in your Etsy app is set to: http://localhost:8000/api/v1/auth/etsy/callback"
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during authentication: {str(e)}")


async def _get_shop_info(access_token: str) -> Optional[dict]:
    """Get shop information using access token"""
    try:
        async with httpx.AsyncClient() as client:
            # First get the user info to get user_id
            user_response = await client.get(
                "https://openapi.etsy.com/v3/application/users/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "x-api-key": settings.ETSY_API_KEY or "",
                },
                timeout=30.0
            )
            user_response.raise_for_status()
            user_data = user_response.json()
            user_id = user_data.get("user_id")
            
            if not user_id:
                print("Could not get user_id from Etsy API")
                return None
            
            # Convert user_id to int (Etsy API requires int in URL path)
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                print(f"Invalid user_id format: {user_id}")
                return None
            print(f"User ID: {user_id_int}")
            # Get user's shops using the user_id (must be int, not string)
            shops_response = await client.get(
                f"https://openapi.etsy.com/v3/application/users/{user_id_int}/shops",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "x-api-key": settings.ETSY_API_KEY or "",
                },
                timeout=30.0
            )
            print(f"Shops response: {shops_response.status_code}")
            print(f"Shops response: {shops_response.json()}")
            shops_response.raise_for_status()
            shops_data = shops_response.json()
            return {
                "id": shops_data.get("shop_id", ""),
                "name": shops_data.get("shop_name", ""),
            }
    except httpx.HTTPStatusError as e:
        print(f"Error getting shop info: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error getting shop info: {e}")
        return None


@router.get("/etsy/status")
async def etsy_status(db: Session = Depends(get_db)):
    """Check Etsy authentication status"""
    token = db.query(OAuthToken).filter(OAuthToken.source == "etsy").first()
    
    if not token:
        return {
            "authenticated": False,
            "message": "Not authenticated with Etsy"
        }
    
    is_expired = token.expires_at and token.expires_at < datetime.utcnow()
    

    print(f"Token: {token}")
    return {
        "authenticated": not is_expired,
        "expired": is_expired,
        "shop_name": token.shop_name,
        "shop_id": token.shop_id,
        "expires_at": token.expires_at.isoformat() if token.expires_at else None,
    }

