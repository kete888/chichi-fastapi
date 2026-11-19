from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Chichi(Base):
    __tablename__ = "chichi"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="主键",
    )
    name: Mapped[str] = mapped_column(
        String(50),
        comment="菜名",
    )
    price: Mapped[float] = mapped_column(
        default=0.0,
        comment="价格",
    )
    description: Mapped[str] = mapped_column(
        String(200),
        default="",
        comment="描述",
    )
    tags: Mapped[str] = mapped_column(
        String(100),
        default="",
        comment="标签，逗号分隔，如：辣,肉,甜",
    )
    intro: Mapped[str] = mapped_column(
        String(500),
        default="",
        comment="美食介绍",
    )
    steps: Mapped[str] = mapped_column(
        String(2000),
        default="",
        comment="制作方法，一行一个步骤",
    )
    video_url: Mapped[str] = mapped_column(
        String(500),
        default="",
        comment="做法视频链接（留空则用菜名去 B 站搜索）",
    )
    image_url: Mapped[str] = mapped_column(
        String(500),
        default="",
        comment="菜品图片地址",
    )

    # create_time / update_time 继承自 Base
