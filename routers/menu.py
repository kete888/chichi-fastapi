from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import chichi as crud
from db.session import get_database
from models.chichi import Chichi
from schemas.chichi import ChichiIn, ChichiOut, ChichiUpdate

router = APIRouter(tags=["menu"])

DbSession = Annotated[AsyncSession, Depends(get_database)]


async def _get_or_404(db: AsyncSession, menu_id: int) -> Chichi:
    """查不到就抛 404，后面的接口都能复用"""
    dish = await crud.get(db, menu_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    return dish


# ========== 1. 添加菜谱 ==========
@router.post("/add_menu", response_model=ChichiOut, status_code=201)
async def add_menu(data: ChichiIn, db: DbSession):
    return await crud.create(db, data)


# ========== 2. 查询单条 ==========
@router.get("/query_menu", response_model=ChichiOut)
async def query_menu(menu_id: int, db: DbSession):
    return await _get_or_404(db, menu_id)


# ========== 5. 查询全部（可按菜名模糊搜索）==========
@router.get("/query_all_menu", response_model=list[ChichiOut])
async def query_all_menu(db: DbSession, name: str | None = None):
    return await crud.list_all(db, name)


# ========== 3. 更新 ==========
@router.put("/update_menu", response_model=ChichiOut)
async def update_menu(menu_id: int, data: ChichiUpdate, db: DbSession):
    dish = await _get_or_404(db, menu_id)
    return await crud.update(db, dish, data)


# ========== 4. 删除 ==========
@router.delete("/delete_menu")
async def delete_menu(menu_id: int, db: DbSession):
    dish = await _get_or_404(db, menu_id)
    await crud.remove(db, dish)
    return {"message": "删除成功", "id": menu_id}
