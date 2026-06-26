"""
作品 ORM 模型
对应 MySQL 作品表: novels
存储作品的核心统计信息和元数据
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, BigInteger, Text
)

from app.database import Base


class Novel(Base):
    """
    作品表模型 (MySQL)

    字段说明:
        id           - 主键自增ID
        novel_uuid   - 作品唯一UUID (业务主键，对外暴露)
        author_id    - 作者用户ID (关联 users.id)
        author_name  - 作者用户名 (冗余存储，避免联表查询)
        title        - 书名/作品名称
        novel_type   - 作品类型/目标读者
        tags         - 标签 (JSON字符串存储，如 ["玄幻","热血"])
        likes        - 点赞量
        views        - 观看量/阅读量
        comments     - 评论量
        created_at   - 创建时间
        updated_at   - 更新时间
    """
    __tablename__ = "novels"

    # ====================== 主键 ======================
    id = Column(Integer, primary_key=True, autoincrement=True, comment="作品自增ID")

    # ====================== 业务主键 ======================
    novel_uuid = Column(
        String(36), unique=True, nullable=False, index=True,
        default=lambda: str(uuid.uuid4()),
        comment="作品唯一UUID"
    )

    # ====================== 作者信息 ======================
    author_id = Column(
        Integer, nullable=False, index=True, comment="作者用户ID"
    )
    author_name = Column(
        String(50), nullable=False, comment="作者用户名"
    )

    # ====================== 作品信息 ======================
    title = Column(
        String(100), nullable=False, comment="书名/作品名称"
    )
    novel_type = Column(
        String(50), nullable=True, comment="作品类型/目标读者"
    )
    tags = Column(
        Text, nullable=True, comment="标签 (JSON字符串)"
    )

    # ====================== 统计字段 ======================
    likes = Column(
        BigInteger, nullable=False, default=0, comment="点赞量"
    )
    views = Column(
        BigInteger, nullable=False, default=0, comment="观看量/阅读量"
    )
    comments = Column(
        BigInteger, nullable=False, default=0, comment="评论量"
    )

    # ====================== 时间戳 ======================
    created_at = Column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    def __repr__(self):
        return f"<Novel(id={self.id}, uuid='{self.novel_uuid}', title='{self.title}', author='{self.author_name}')>"

    def to_dict(self) -> dict:
        """
        转换为字典

        Returns:
            dict: 作品信息字典
        """
        return {
            "id": self.id,
            "novel_uuid": self.novel_uuid,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "title": self.title,
            "novel_type": self.novel_type,
            "tags": self.tags,
            "likes": self.likes,
            "views": self.views,
            "comments": self.comments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
