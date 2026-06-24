"""
用户管理服务模块
封装用户信息管理的业务逻辑
"""
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from app.dao.user_dao import UserDAO
from app.models.user import User
from app.application.dto import UserResponse, UpdateUserRequest


class UserService:
    """
    用户管理服务层
    处理用户信息的增删改查业务逻辑
    """

    # ====================== 查询操作 ======================

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[UserResponse]:
        """获取单个用户信息"""
        user = UserDAO.get_by_id(db, user_id)
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserResponse]:
        """根据用户名获取用户信息"""
        user = UserDAO.get_by_username(db, username)
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    def list_users(
        db: Session,
        page: int = 1,
        size: int = 20,
        status: Optional[int] = None,
    ) -> Tuple[List[UserResponse], int]:
        """
        分页获取用户列表

        Args:
            db:     数据库会话
            page:   页码 (从1开始)
            size:   每页数量
            status: 按状态筛选

        Returns:
            (用户列表, 总数)
        """
        skip = (page - 1) * size
        users = UserDAO.get_all(db, skip=skip, limit=size, status=status)
        total = UserDAO.count(db, status=status)

        return [UserResponse.model_validate(u) for u in users], total

    # ====================== 更新操作 ======================

    @staticmethod
    def update_user(
        db: Session, user: User, req: UpdateUserRequest
    ) -> Tuple[Optional[UserResponse], Optional[str]]:
        """
        更新用户信息（部分更新）

        Args:
            db:   数据库会话
            user: 要更新的用户对象
            req:  更新数据（仅更新非 None 字段）

        Returns:
            (UserResponse, None)  更新成功
            (None, "错误信息")     更新失败
        """
        update_fields = req.model_dump(exclude_unset=True)

        if not update_fields:
            return None, "没有需要更新的字段"

        for field, value in update_fields.items():
            setattr(user, field, value)

        user = UserDAO.update(db, user)
        return UserResponse.model_validate(user), None

    @staticmethod
    def update_user_by_admin(
        db: Session, target_user: User, req: UpdateUserRequest
    ) -> Tuple[Optional[UserResponse], Optional[str]]:
        """
        管理员更新用户信息（可修改更多字段）
        """
        return UserService.update_user(db, target_user, req)

    # ====================== 删除操作 ======================

    @staticmethod
    def delete_user(db: Session, user: User) -> bool:
        """
        删除用户（物理删除）

        Args:
            db:   数据库会话
            user: 要删除的用户

        Returns:
            操作是否成功
        """
        try:
            UserDAO.delete(db, user)
            return True
        except Exception:
            return False
