import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """把所有全局异常处理集中注册到 app 上"""

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        # 数据库约束错误（唯一索引、外键、非空…）
        # 详细原因只进日志，不给用户看表结构
        logger.warning("IntegrityError %s: %s", request.url.path, exc.orig)
        return JSONResponse(
            status_code=409,
            content={"detail": "数据冲突，请检查是否重复"},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # 兜底：连接断了、程序 bug 等
        logger.exception("未处理异常 %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器开小差了，请稍后再试"},
        )
