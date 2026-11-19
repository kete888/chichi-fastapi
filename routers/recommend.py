from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core import solar_terms
from crud import chichi as crud
from db.session import get_database
from schemas.chichi import ChichiOut
from schemas.solar_term import SolarTermOut

router = APIRouter(prefix="/recommend", tags=["recommend"])

DbSession = Annotated[AsyncSession, Depends(get_database)]
Limit = Annotated[int, Query(ge=1, le=50, description="返回条数")]

# 心情 → 需要的标签
# 想加新心情，只改这里，前端按钮会自动跟着变
MOOD_MAP = {
    "开心": "辣",
    "不开心": "甜",
    "累了": "汤",
    "饿了": "肉",
    "想减脂": "素",
    "赶时间": "快",
}


# ========== 随机推荐（小表版本）==========
@router.get("/simple", response_model=list[ChichiOut])
async def recommend_simple(db: DbSession, limit: Limit = 5):
    return await crud.random_dishes(db, limit)


# ========== 可选心情列表 ==========
@router.get("/moods")
async def list_moods():
    return [{"mood": k, "tag": v} for k, v in MOOD_MAP.items()]


# ========== 按心情推荐 ==========
@router.get("/mood", response_model=list[ChichiOut])
async def recommend_by_mood(mood: str, db: DbSession, limit: Limit = 1):
    tag = MOOD_MAP.get(mood)
    if tag is None:
        raise HTTPException(
            status_code=400,
            detail=f"没有这个心情，可选：{'、'.join(MOOD_MAP)}",
        )

    rows = await crud.random_dishes_with_tag(db, tag, limit)
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"还没有「{mood}」对应的菜谱（需要标签包含「{tag}」）",
        )
    return rows


# ========== 二十四节气 ==========
@router.get("/solar-terms")
async def list_solar_terms():
    """返回全部节气，以及今天属于哪个节气"""
    today = solar_terms.current()
    return {
        "current": today.name,
        "today": date.today().isoformat(),
        "items": [
            {
                "name": t.name,
                "date": t.date_str,
                "season": t.season,
                "foods": list(t.foods),
            }
            for t in solar_terms.SOLAR_TERMS
        ],
    }


@router.get("/solar-term", response_model=SolarTermOut)
async def recommend_by_solar_term(
    db: DbSession,
    term: str | None = None,
    limit: Limit = 5,
):
    """按节气推荐：不传 term 就用今天所属的节气"""
    if term:
        st = solar_terms.find(term)
        if st is None:
            names = "、".join(t.name for t in solar_terms.SOLAR_TERMS)
            raise HTTPException(status_code=404, detail=f"没有这个节气，可选：{names}")
    else:
        st = solar_terms.current()

    dishes = await crud.recommend_for_term(
        db, list(st.keywords), list(st.tags), limit
    )

    return {
        "name": st.name,
        "date": st.date_str,
        "season": st.season,
        "foods": list(st.foods),
        "dishes": dishes,
    }
