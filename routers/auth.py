from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.auth import COOKIE_NAME, check_password, create_token
from core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter(tags=["auth"], include_in_schema=False)


class LoginIn(BaseModel):
    username: str
    password: str


@router.get("/login")
async def login_page():
    if not settings.auth_enabled:
        return FileResponse(BASE_DIR / "templates" / "index.html")
    return FileResponse(BASE_DIR / "templates" / "login.html")


@router.post("/login")
async def login(data: LoginIn, response: Response):
    if not check_password(data.username, data.password):
        raise HTTPException(status_code=401, detail="用户名或密码不对")

    response.set_cookie(
        key=COOKIE_NAME,
        value=create_token(data.username),
        max_age=settings.session_hours * 3600,
        httponly=True,
        samesite="lax",
    )
    return {"ok": True}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
async def me():
    return {"username": settings.admin_username}
