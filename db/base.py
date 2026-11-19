from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有表共有的字段：写在基类里，子类自动继承"""

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now(),
        comment="创建时间",
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        onupdate=func.now(),
        default=func.now(),
        comment="更新时间",
    )
