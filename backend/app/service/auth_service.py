"""
认证服务模块
包含用户登录、注册、Token管理等核心认证业务逻辑
"""
from datetime import timedelta
from typing import Optional, Tuple

import bcrypt
from sqlalchemy.orm import Session

from app.config import settings
from app.dao.user_dao import UserDAO
from app.models.user import User
from app.application.jwt_handler import create_access_token, decode_access_token
from app.application.dto import (
    LoginRequest, RegisterRequest,
    UserResponse, LoginResponse, TokenPayload,
)


class AuthService:
    """
    认证服务层
    封装用户认证相关的所有业务逻辑
    """

    # ====================== 密码处理 ======================

    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行 bcrypt 哈希"""
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=settings.PASSWORD_HASH_ROUNDS),
        ).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证明文密码与哈希密码是否匹配"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    # ====================== 用户注册 ======================

    @staticmethod
    def register(db: Session, req: RegisterRequest) -> Tuple[Optional[UserResponse], Optional[str]]:
        """
        用户注册

        Args:
            db:  数据库会话
            req: 注册请求数据

        Returns:
            (UserResponse, None) 注册成功
            (None, "错误信息")    注册失败
        """
        # 1. 检查用户名是否已存在
        existing = UserDAO.get_by_username(db, req.username)
        if existing:
            return None, f"用户名 '{req.username}' 已被注册"

        # 2. 检查邮箱是否已被使用
        if req.email:
            existing_email = UserDAO.get_by_email(db, req.email)
            if existing_email:
                return None, f"邮箱 '{req.email}' 已被注册"

        # 3. 创建用户对象
        user = User(
            username=req.username,
            password=AuthService.hash_password(req.password),
            email=req.email,
            phone=req.phone,
            status=1,
            superuser=0,
        )

        # 4. 持久化
        user = UserDAO.create(db, user)
        return UserResponse.model_validate(user), None

    # ====================== 用户登录 ======================

    @staticmethod
    def login(db: Session, req: LoginRequest) -> Tuple[Optional[LoginResponse], Optional[str]]:
        """
        用户登录

        流程:
            1. 查询用户
            2. 校验密码
            3. 检查账号状态
            4. 生成 JWT Token
            5. 更新数据库中的 Token

        Args:
            db:  数据库会话
            req: 登录请求

        Returns:
            (LoginResponse, None) 登录成功
            (None, "错误信息")      登录失败
        """
        # 1. 查询用户
        user = UserDAO.get_by_username(db, req.username)
        if not user:
            return None, "用户名或密码错误"

        # 2. 校验密码
        if not AuthService.verify_password(req.password, user.password):
            return None, "用户名或密码错误"

        # 3. 检查账号状态
        if user.status != 1:
            return None, "账号已被禁用，请联系管理员"

        # 4. 生成 JWT Token
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            superuser=user.superuser,
        )

        # 5. 更新数据库中的 Token（可用于服务端 Token 管理）
        UserDAO.update_token(db, user, access_token)

        # 6. 构造响应
        return LoginResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        ), None

    # ====================== Token 校验 ======================

    @staticmethod
    def verify_token(token: str) -> Tuple[Optional[TokenPayload], Optional[str]]:
        """
        校验 JWT Token

        Args:
            token: JWT 令牌字符串

        Returns:
            (TokenPayload, None)   令牌有效
            (None, "错误信息")      令牌无效
        """
        return decode_access_token(token)

    # ====================== 用户登出 ======================

    @staticmethod
    def logout(db: Session, user: User) -> bool:
        """
        用户登出 - 清除数据库中的 Token

        Args:
            db:   数据库会话
            user: 当前用户

        Returns:
            操作是否成功
        """
        try:
            UserDAO.update_token(db, user, None)
            return True
        except Exception:
            return False

    # ====================== 修改密码 ======================

    @staticmethod
    def change_password(
        db: Session, user: User, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        修改用户密码

        Args:
            db:           数据库会话
            user:         当前用户
            old_password: 旧密码
            new_password: 新密码

        Returns:
            (True, None)         修改成功
            (False, "错误信息")   修改失败
        """
        # 1. 校验旧密码
        if not AuthService.verify_password(old_password, user.password):
            return False, "旧密码不正确"

        # 2. 更新密码
        user.password = AuthService.hash_password(new_password)
        UserDAO.update(db, user)
        return True, None
