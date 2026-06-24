"""
API 依赖注入模块
提供通用依赖函数（如获取当前登录用户）
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.dao.user_dao import UserDAO
from app.models.user import User
from app.application.jwt_handler import decode_access_token

# HTTP Bearer Token 安全方案
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户（必须登录）

    流程:
        1. 从 Authorization Header 提取 Token
        2. 解析 JWT 获取用户信息
        3. 从数据库查询用户并校验状态

    Raises:
        HTTPException 401: 未认证或 Token 无效
        HTTPException 403: 账号已被禁用

    Returns:
        User: 当前登录用户
    """
    # 检查是否提供了 Token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # 解析 JWT
    payload, error = decode_access_token(token)
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 查询用户
    user = UserDAO.get_by_id(db, payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 检查状态
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员",
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    获取当前用户（可选，未登录也允许访问）

    Returns:
        Optional[User]: 登录用户或 None
    """
    if credentials is None:
        return None

    payload, error = decode_access_token(credentials.credentials)
    if error:
        return None

    user = UserDAO.get_by_id(db, payload.user_id)
    if not user or user.status != 1:
        return None

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前超级管理员用户（必须登录且为超级管理员）

    Raises:
        HTTPException 403: 非超级管理员

    Returns:
        User: 当前超级管理员用户
    """
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限",
        )
    return current_user
