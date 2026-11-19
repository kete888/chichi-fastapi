"""应用入口：只负责「组装」，不写业务、不写 SQL。

启动方式：
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from core.auth import COOKIE_NAME, verify_token
from core.config import settings
from core.exceptions import register_exception_handlers
from db.base import Base
from db.session import async_engine
from models.chichi import Chichi  # noqa: F401  必须导入，模型才会注册到 metadata
from routers import auth, menu, recommend

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("服务启动")

    yield

    # 关闭：释放连接池
    await async_engine.dispose()
    print("服务关闭")


app = FastAPI(lifespan=lifespan, title=settings.app_title)

# 全局异常处理
register_exception_handlers(app)

# 允许 file:// 打开的前端页面跨域访问（仅本地开发用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态资源
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# 登录拦截：没登录时，页面跳登录页，接口返回 401
PUBLIC_PATHS = {"/login", "/logout"}


@app.middleware("http")
async def auth_guard(request: Request, call_next):
    if not settings.auth_enabled or request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path
    if path in PUBLIC_PATHS or path.startswith("/static"):
        return await call_next(request)

    if verify_token(request.cookies.get(COOKIE_NAME)):
        return await call_next(request)

    if path == "/":
        return RedirectResponse(url="/login", status_code=303)
    return JSONResponse({"detail": "未登录"}, status_code=401)


# 路由
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(recommend.router)


@app.get("/", include_in_schema=False)
async def index():
    """首页：返回前端页面"""
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/info")
async def info():
    """接口清单"""
    return {
        "message": "欢迎来到吃了吗管理系统",
        "功能列表": {
            "1.添加菜谱信息": "/add_menu",
            "2.查询菜单信息": "/query_menu",
            "3.更新菜单信息": "/update_menu",
            "4.删除菜单信息": "/delete_menu",
            "5.查询所有菜单信息": "/query_all_menu",
            "6.随机推荐": "/recommend/simple",
            "7.按心情推荐": "/recommend/mood",
        },
    }
