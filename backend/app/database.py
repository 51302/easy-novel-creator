"""
数据库连接管理模块
使用 SQLAlchemy 管理 MySQL 数据库连接
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings


# ====================== 数据库引擎 ======================
engine = create_engine(
    settings.SYNC_DATABASE_URL,
    pool_size=20,               # 连接池大小
    max_overflow=10,            # 最大溢出连接
    pool_pre_ping=True,         # 每次从池中取出连接时先 ping 检测有效性
    pool_recycle=3600,          # 连接回收时间 (秒)
    echo=settings.DEBUG,        # 开发环境打印 SQL
)

# ====================== 会话工厂 ======================
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ====================== 声明式基类 ======================
class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass


def get_db():
    """
    获取数据库会话的依赖注入函数
    使用 yield 确保请求结束后正确关闭会话

    Yields:
        Session: 数据库会话实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库表结构
    根据所有继承 Base 的模型自动创建数据库表
    """
    Base.metadata.create_all(bind=engine)
