from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 放在项目根目录（不管从哪个目录启动都能找到）
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """全部配置集中在这里，自动从 .env / 环境变量读取"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_title: str = "今天吃啥？"

    # 数据库（必须在 .env 里配置，代码中不留默认值）
    async_database_url: str

    # 连接池
    db_echo: bool = False          # 打印 SQL
    db_pool_size: int = 10         # 常驻连接数
    db_max_overflow: int = 20      # 允许额外超出的连接数
    db_pool_recycle: int = 3600    # 连接回收时间（秒）

    # 登录（密码和密钥必须在 .env 里配置）
    auth_enabled: bool = True
    admin_username: str = "admin"
    admin_password: str
    secret_key: str
    session_hours: int = 72        # 登录有效期（小时）


settings = Settings()
