"""Google OAuth authentication"""

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from server.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_CALLBACK_URL, ADMIN_EMAIL, APP_URL

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/google")
async def google_login():
    """Redirect to Google OAuth."""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_CALLBACK_URL,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"{GOOGLE_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(request: Request, code: str = ""):
    """Handle Google OAuth callback."""
    if not code:
        return RedirectResponse(f"{APP_URL}?error=no_code")

    # Exchange code for token
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_CALLBACK_URL,
            "grant_type": "authorization_code",
        })

        if token_resp.status_code != 200:
            return RedirectResponse(f"{APP_URL}?error=token_exchange_failed")

        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        # Get user info
        user_resp = await client.get(GOOGLE_USERINFO_URL, headers={
            "Authorization": f"Bearer {access_token}"
        })

        if user_resp.status_code != 200:
            return RedirectResponse(f"{APP_URL}?error=userinfo_failed")

        user_info = user_resp.json()

    email = user_info.get("email", "")

    # Only allow admin email
    if email.lower() != ADMIN_EMAIL.lower():
        return RedirectResponse(f"{APP_URL}?error=unauthorized")

    # Set session
    request.session["user"] = {
        "email": email,
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", ""),
    }

    return RedirectResponse(APP_URL)


@router.get("/me")
async def me(request: Request):
    """Get current user."""
    user = request.session.get("user")
    if not user:
        return JSONResponse({"authenticated": False}, status_code=401)
    return {"authenticated": True, "user": user}


@router.post("/logout")
async def logout(request: Request):
    """Clear session."""
    request.session.clear()
    return {"ok": True}
