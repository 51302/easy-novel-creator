"""
用户数据访问对象 (Data Access Object)
负责与数据库的直接交互，封装所有 CRUD 操作
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.user import User


class UserDAO:
    """
    用户表 DAO
    纯数据访问层，不包含任何业务逻辑
    """

    # ====================== 查询操作 ======================

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据 ID 查询用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱查询用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        """根据手机号查询用户"""
        return db.query(User).filter(User.phone == phone).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None,
    ) -> List[User]:
        """
        分页查询用户列表

        Args:
            db:     数据库会话
            skip:   跳过记录数（分页偏移）
            limit:  返回记录数上限
            status: 按状态筛选（None=全部）

        Returns:
            用户列表
        """
        query = db.query(User)
        if status is not None:
            query = query.filter(User.status == status)
        return query.order_by(User.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session, status: Optional[int] = None) -> int:
        """统计用户总数"""
        query = db.query(User)
        if status is not None:
            query = query.filter(User.status == status)
        return query.count()

    # ====================== 写入操作 ======================

    @staticmethod
    def create(db: Session, user: User) -> User:
        """创建用户"""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: User) -> User:
        """更新用户"""
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        """删除用户（物理删除）"""
        db.delete(user)
        db.commit()

    # ====================== 业务辅助查询 ======================

    @staticmethod
    def update_token(db: Session, user: User, token: Optional[str]) -> User:
        """更新用户的 JWT Token"""
        user.token = token
        db.commit()
        db.refresh(user)
        return user
