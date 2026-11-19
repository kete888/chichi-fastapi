from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

# 全局唯一的异步引擎（内部持有连接池），整个进程只建一次
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
)

# 会话工厂：调用一次造一个会话，本身不做任何数据库连接
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,   # 提交后对象属性不过期，避免异步下触发隐式 IO
)


async def get_database() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：只负责借出和归还。

    - 交出 session
    - 退出 async with 时自动 close（未提交的事务会自动回滚）
    - commit 由各个写接口自己负责
    """
    async with AsyncSessionLocal() as session:
        yield session
