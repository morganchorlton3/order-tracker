import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.oauth_token import OAuthToken


class EtsyService:
    def __init__(self, db: Optional[Session] = None, user_id: Optional[int] = None):
        self.api_key = settings.ETSY_API_KEY
        self.api_secret = settings.ETSY_API_SECRET
        self.redirect_uri = settings.ETSY_REDIRECT_URI
        self.base_url = "https://openapi.etsy.com/v3"
        self.db = db
        self.user_id = user_id

    def get_access_token(self) -> Optional[str]:
        """Get the current access token from database"""
        if not self.db or not self.user_id:
            return None
        
        try:
            token = self.db.query(OAuthToken).filter(
                OAuthToken.source == "etsy",
                OAuthToken.user_id == self.user_id
            ).first()
            
            if not token:
                return None
            
            # Check if token is expired
            if token.expires_at and token.expires_at < datetime.utcnow():
                # Token expired, try to refresh
                if token.refresh_token:
                    return self._refresh_token(token)
                return None
            
            return token.access_token
        except Exception as e:
            # Handle case where oauth_tokens table doesn't exist yet
            print(f"Error getting access token (table may not exist): {e}")
            return None

    def _refresh_token(self, token: OAuthToken) -> Optional[str]:
        """Refresh the access token using refresh token"""
        # TODO: Implement token refresh
        # For now, return None if expired
        return None

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to Etsy API"""
        access_token = self.get_access_token()
        
        if not access_token:
            raise ValueError("No valid access token. Please authenticate with Etsy first.")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.api_key or "",
        }
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_shop_id(self) -> Optional[int]:
        """Get the authenticated user's shop ID"""
        token = None
        # First try to get from stored token
        if self.db:
            try:
                token = self.db.query(OAuthToken).filter(
                    OAuthToken.source == "etsy"
                ).first()
                if token and token.shop_id:
                    try:
                        return int(token.shop_id)
                    except (ValueError, TypeError):
                        pass
            except Exception as e:
                # Handle case where oauth_tokens table doesn't exist yet
                error_msg = str(e)
                if "does not exist" in error_msg or "UndefinedTable" in error_msg:
                    raise ValueError(
                        "OAuth tokens table not found. Please run database migrations: "
                        "alembic upgrade head"
                    )
                print(f"Error querying oauth_tokens table: {e}")
        
        # If not in token, fetch from API
        try:
            # First get the user info to get user_id
            user_response = await self._make_request("GET", "/application/users/me")
            user_id = user_response.get("user_id")
            
            if not user_id:
                raise ValueError("Could not get user_id from Etsy API")
            
            # Convert user_id to int (Etsy API requires int in URL path)
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid user_id format: {user_id}")
            
            # Get user's shops using the user_id (must be int)
            response = await self._make_request("GET", f"/application/users/{user_id_int}/shops")
            shops = response.get("results", [])
            if shops:
                shop_id = shops[0].get("shop_id")
                shop_name = shops[0].get("shop_name", "")
                # Update token with shop_id if we have a db session
                if self.db and token:
                    try:
                        token.shop_id = str(shop_id)
                        if shop_name and not token.shop_name:
                            token.shop_name = shop_name
                        self.db.commit()
                    except Exception as e:
                        self.db.rollback()
                        print(f"Error updating token with shop_id: {e}")
                return shop_id
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Authentication failed. Your access token may have expired. "
                    "Please re-authenticate by visiting: /api/v1/auth/etsy/authorize"
                )
            raise ValueError(f"Error getting shop ID from Etsy API: {e.response.text}")
        except Exception as e:
            error_msg = str(e)
            if "No valid access token" in error_msg:
                raise ValueError(
                    "No valid access token. Please authenticate first by visiting: "
                    "/api/v1/auth/etsy/authorize"
                )
            raise ValueError(f"Error getting shop ID: {error_msg}")

    async def fetch_orders(self, shop_id: Optional[int] = None, min_created: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch orders (receipts) from Etsy API"""
        # Check if we have an access token first
        access_token = self.get_access_token()
        if not access_token:
            raise ValueError(
                "No Etsy access token found. Please authenticate first by visiting: "
                "/api/v1/auth/etsy/authorize and completing the OAuth flow."
            )
        
        if not shop_id:
            shop_id = await self.get_shop_id()
        
        if not shop_id:
            raise ValueError(
                "Could not determine shop ID. Please ensure you're authenticated. "
                "Visit /api/v1/auth/etsy/status to check your authentication status."
            )
        
        all_receipts = []
        limit = 100
        offset = 0
        
        try:
            while True:
                params = {
                    "limit": limit,
                    "offset": offset,
                }
                
                if min_created:
                    params["min_created"] = min_created
                
                response = await self._make_request(
                    "GET",
                    f"/application/shops/{shop_id}/receipts",
                    params=params
                )
                
                receipts = response.get("results", [])
                if not receipts:
                    break
                
                all_receipts.extend(receipts)
                
                # Check if there are more pages
                if len(receipts) < limit:
                    break
                
                offset += limit
            
            return all_receipts
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Authentication failed. Please re-authenticate with Etsy.")
            raise
        except Exception as e:
            raise ValueError(f"Error fetching orders from Etsy: {str(e)}")

    async def get_receipt_details(self, receipt_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific receipt"""
        try:
            response = await self._make_request("GET", f"/application/shops/receipts/{receipt_id}")
            return response
        except Exception as e:
            raise ValueError(f"Error fetching receipt details: {str(e)}")

    def transform_receipt_to_order(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Etsy receipt data to our Order model format"""
        # Extract customer information
        buyer_name = receipt.get("name", "")
        buyer_email = receipt.get("buyer_email", "")
        
        # Extract shipping address
        shipping_address = {
            "name": receipt.get("name", ""),
            "first_line": receipt.get("first_line", ""),
            "second_line": receipt.get("second_line", ""),
            "city": receipt.get("city", ""),
            "state": receipt.get("state", ""),
            "zip": receipt.get("zip", ""),
            "country": receipt.get("country_iso", ""),
        }
        
        # Extract order items
        transactions = receipt.get("transactions", [])
        items = []
        for transaction in transactions:
            items.append({
                "transaction_id": transaction.get("transaction_id"),
                "listing_id": transaction.get("listing_id"),
                "title": transaction.get("title", ""),
                "quantity": transaction.get("quantity", 1),
                "price": float(transaction.get("price", {}).get("amount", 0)) / 100,  # Etsy uses cents
                "currency": transaction.get("price", {}).get("currency_code", "USD"),
            })
        
        # Calculate total amount
        total_amount = float(receipt.get("total_price", {}).get("amount", 0)) / 100
        currency = receipt.get("total_price", {}).get("currency_code", "USD")
        
        # Map Etsy status to our status
        was_paid = receipt.get("was_paid", False)
        was_shipped = receipt.get("was_shipped", False)
        is_delivered = receipt.get("is_delivered", False)
        is_cancelled = receipt.get("is_cancelled", False)
        
        if is_cancelled:
            status = "cancelled"
        elif is_delivered:
            status = "delivered"
        elif was_shipped:
            status = "shipped"
        elif was_paid:
            status = "processing"
        else:
            status = "pending"
        
        # Parse order date
        created_timestamp = receipt.get("creation_timestamp", 0)
        order_date = datetime.fromtimestamp(created_timestamp / 1000) if created_timestamp else datetime.utcnow()
        
        return {
            "external_id": str(receipt.get("receipt_id")),
            "source": "etsy",
            "status": status,
            "customer_name": buyer_name,
            "customer_email": buyer_email if buyer_email else None,
            "shipping_address": shipping_address,
            "total_amount": total_amount,
            "currency": currency,
            "items": items,
            "order_date": order_date,
        }

    async def create_listing(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a product listing on Etsy"""
        # TODO: Implement product creation on Etsy
        # This requires shop_id and specific Etsy listing format
        raise NotImplementedError("Product creation not yet implemented")

    async def update_listing(self, listing_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product listing on Etsy"""
        # TODO: Implement product update on Etsy
        raise NotImplementedError("Product update not yet implemented")
