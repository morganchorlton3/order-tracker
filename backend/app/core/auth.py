from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe.session.framework.fastapi import verify_session
from app.core.config import settings

# Prepare supertokens_config
supertokens_config_kwargs = {
    "connection_uri": settings.SUPERTOKENS_CONNECTION_URI,
}

# Add API key if provided (required for deployed cores)
if settings.SUPERTOKENS_API_KEY:
    supertokens_config_kwargs["api_key"] = settings.SUPERTOKENS_API_KEY

supertokens_config = SupertokensConfig(**supertokens_config_kwargs)

# Initialize SuperTokens
init(
    app_info=InputAppInfo(
        app_name="Order Tracker",
        api_domain=f"http://{settings.SUPERTOKENS_API_DOMAIN}:8000",
        website_domain=settings.SUPERTOKENS_WEBSITE_DOMAIN,
        api_base_path="/auth",
        website_base_path="/auth"
    ),
    supertokens_config=supertokens_config,
    framework="fastapi",
    recipe_list=[
        emailpassword.init(),
        session.init(),
    ],
)

# Middleware for SuperTokens
supertokens_middleware = get_middleware()

# Dependency to get session
# verify_session() returns a dependency function that FastAPI will handle
get_session = verify_session()

