"""菜谱的数据库操作层。

这一层只和数据库打交道：不处理 HTTP、不抛 HTTPException。
路由负责判断「找不到就 404」，这里只返回 None。
"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chichi import Chichi
from schemas.chichi import ChichiIn, ChichiUpdate


async def get(db: AsyncSession, dish_id: int) -> Chichi | None:
    """按 id 查一条，找不到返回 None"""
    return await db.get(Chichi, dish_id)


async def list_all(db: AsyncSession, name: str | None = None) -> list[Chichi]:
    """查全部，可按菜名模糊搜索"""
    stmt = select(Chichi)
    if name:
        stmt = stmt.where(Chichi.name.contains(name))
    stmt = stmt.order_by(Chichi.id)
    return list((await db.scalars(stmt)).all())


async def create(db: AsyncSession, data: ChichiIn) -> Chichi:
    """新增一条，返回带 id 和时间的完整对象"""
    dish = Chichi(**data.model_dump())
    db.add(dish)
    await db.commit()
    await db.refresh(dish)
    return dish


async def update(db: AsyncSession, dish: Chichi, data: ChichiUpdate) -> Chichi:
    """只更新请求里传了的字段"""
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dish, key, value)
    await db.commit()
    await db.refresh(dish)
    return dish


async def remove(db: AsyncSession, dish: Chichi) -> None:
    await db.delete(dish)
    await db.commit()


async def random_dishes(db: AsyncSession, limit: int) -> list[Chichi]:
    """整表随机取 N 条"""
    stmt = select(Chichi).order_by(func.rand()).limit(limit)
    return list((await db.scalars(stmt)).all())


async def random_dishes_with_tag(db: AsyncSession, tag: str, limit: int) -> list[Chichi]:
    """只在含有指定标签的菜里随机取 N 条"""
    stmt = (
        select(Chichi)
        .where(Chichi.tags.contains(tag))
        .order_by(func.rand())
        .limit(limit)
    )
    return list((await db.scalars(stmt)).all())


async def recommend_for_term(
    db: AsyncSession,
    keywords: list[str],
    tags: list[str],
    limit: int,
) -> list[Chichi]:
    """节气推荐：先按菜名关键词找，找不到再用标签兜底"""
    if keywords:
        stmt = (
            select(Chichi)
            .where(or_(*[Chichi.name.contains(k) for k in keywords]))
            .order_by(func.rand())
            .limit(limit)
        )
        rows = list((await db.scalars(stmt)).all())
        if rows:
            return rows

    if tags:
        stmt = (
            select(Chichi)
            .where(or_(*[Chichi.tags.contains(t) for t in tags]))
            .order_by(func.rand())
            .limit(limit)
        )
        return list((await db.scalars(stmt)).all())

    return []
