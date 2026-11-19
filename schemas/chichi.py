from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChichiIn(BaseModel):
    """新增菜谱时接收的数据"""
    name: str = Field(min_length=1, max_length=50, description="菜名")
    price: float = Field(default=0.0, ge=0, description="价格")
    description: str = Field(default="", max_length=200, description="一句话简介")
    tags: str = Field(default="", max_length=100, description="标签，逗号分隔，如：辣,肉")
    intro: str = Field(default="", max_length=500, description="美食介绍")
    steps: str = Field(default="", max_length=2000, description="制作方法，一行一步")
    video_url: str = Field(default="", max_length=500, description="做法视频链接")
    image_url: str = Field(default="", max_length=500, description="菜品图片地址")


class ChichiUpdate(BaseModel):
    """更新菜谱时接收的数据（全部可选，只改传了的字段）"""
    name: str | None = Field(default=None, min_length=1, max_length=50)
    price: float | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=200)
    tags: str | None = Field(default=None, max_length=100)
    intro: str | None = Field(default=None, max_length=500)
    steps: str | None = Field(default=None, max_length=2000)
    video_url: str | None = Field(default=None, max_length=500)
    image_url: str | None = Field(default=None, max_length=500)


class ChichiOut(BaseModel):
    """返回给前端的数据"""
    # 允许直接读取 ORM 对象（Chichi 实例）的属性
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    description: str
    tags: str
    intro: str
    steps: str
    video_url: str
    image_url: str
    create_time: datetime
