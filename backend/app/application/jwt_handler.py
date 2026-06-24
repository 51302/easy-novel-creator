"""
JWT 令牌处理模块
负责 JWT 的生成、解析和校验
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.config import settings
from app.application.dto import TokenPayload


# ====================== JWT 令牌生成 ======================

def create_access_token(
    user_id: int,
    username: str,
    superuser: int = 0,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    生成 JWT 访问令牌

    Args:
        user_id:       用户ID
        username:      用户名
        superuser:     是否超级管理员
        expires_delta: 自定义过期时间（默认使用配置文件的值）

    Returns:
        str: 编码后的 JWT 字符串
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.utcnow()
    payload = {
        "sub":       username,                              # subject = 用户名
        "user_id":   user_id,
        "superuser": superuser,
        "iat":       now,                                   # 签发时间
        "exp":       now + expires_delta,                   # 过期时间
        "type":      "access",                              # 令牌类型
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ====================== JWT 令牌解析 ======================

def decode_access_token(token: str) -> Tuple[Optional[TokenPayload], Optional[str]]:
    """
    解析并校验 JWT 访问令牌

    Args:
        token: JWT 令牌字符串

    Returns:
        Tuple[Optional[TokenPayload], Optional[str]]:
            - 成功: (TokenPayload, None)
            - 失败: (None, "错误信息")
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # 校验令牌类型
        if payload.get("type") != "access":
            return None, "无效的令牌类型"

        token_data = TokenPayload(
            sub=payload.get("sub"),
            user_id=payload.get("user_id"),
            superuser=payload.get("superuser", 0),
        )
        return token_data, None

    except ExpiredSignatureError:
        return None, "令牌已过期，请重新登录"
    except InvalidTokenError:
        return None, "无效的令牌"
    except Exception as e:
        return None, f"令牌解析失败: {str(e)}"
