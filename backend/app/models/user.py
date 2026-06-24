"""
用户 ORM 模型
对应 MySQL 用户表: users
"""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, SmallInteger
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    用户表模型

    字段说明:
        id        - 主键自增ID
        username  - 用户名（唯一）
        password  - 加密后的密码
        token     - JWT Token（登录时生成，可用于黑名单/白名单校验）
        status    - 用户状态: 0=禁用, 1=正常
        email     - 邮箱
        phone     - 手机号
        superuser - 是否超级管理员: 0=否, 1=是
    """
    __tablename__ = "users"

    # ====================== 主键 ======================
    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")

    # ====================== 核心字段 ======================
    username = Column(
        String(50), unique=True, nullable=False, index=True, comment="用户名"
    )
    password = Column(
        String(255), nullable=False, comment="密码（bcrypt 加密）"
    )
    token = Column(
        String(500), nullable=True, default=None, comment="当前JWT Token"
    )

    # ====================== 状态与权限 ======================
    status = Column(
        SmallInteger, nullable=False, default=1, comment="状态: 0=禁用, 1=正常"
    )
    superuser = Column(
        SmallInteger, nullable=False, default=0, comment="超级管理员: 0=否, 1=是"
    )

    # ====================== 联系信息 ======================
    email = Column(
        String(100), nullable=True, default=None, comment="邮箱"
    )
    phone = Column(
        String(20), nullable=True, default=None, comment="手机号"
    )

    # ====================== 时间戳 ======================
    created_at = Column(
        DateTime, default=datetime.utcnow, comment="创建时间"
    )
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', superuser={self.superuser})>"

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典（默认排除敏感字段）

        Args:
            include_sensitive: 是否包含密码、token 等敏感字段

        Returns:
            dict: 用户信息字典
        """
        data = {
            "id": self.id,
            "username": self.username,
            "status": self.status,
            "email": self.email,
            "phone": self.phone,
            "superuser": self.superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_sensitive:
            data["token"] = self.token
        return data
