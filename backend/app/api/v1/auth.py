"""
认证接口模块
提供登录、注册、登出、密码修改等 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.service.auth_service import AuthService
from app.application.dto import (
    LoginRequest, RegisterRequest,
    LoginResponse, UserResponse,
    ChangePasswordRequest, StandardResponse,
)

router = APIRouter(prefix="/auth", tags=["认证"])


# ====================== 用户注册 ======================

@router.post("/register", response_model=StandardResponse, summary="用户注册")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口

    - **username**: 用户名（2-50字符，字母数字下划线）
    - **password**: 密码（6-128字符）
    - **email**: 邮箱（可选）
    - **phone**: 手机号（可选）
    """
    user, error = AuthService.register(db, req)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(
        code=201,
        message="注册成功",
        data=user.model_dump(),
    )


# ====================== 用户登录 ======================

@router.post("/login", response_model=StandardResponse, summary="用户登录")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口

    验证用户名密码，返回 JWT 令牌和用户信息

    - **username**: 用户名
    - **password**: 密码
    """
    result, error = AuthService.login(db, req)
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
        )

    return StandardResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": result.access_token,
            "token_type": result.token_type,
            "user": result.user.model_dump(),
        },
    )


# ====================== 用户登出 ======================

@router.post("/logout", response_model=StandardResponse, summary="用户登出")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    用户登出接口（需登录）

    清除服务端的 JWT Token
    """
    AuthService.logout(db, current_user)
    return StandardResponse(message="登出成功")


# ====================== 修改密码 ======================

@router.put("/password", response_model=StandardResponse, summary="修改密码")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改当前用户密码（需登录）

    - **old_password**: 旧密码
    - **new_password**: 新密码
    """
    success, error = AuthService.change_password(
        db, current_user, req.old_password, req.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(message="密码修改成功")


# ====================== 获取当前用户信息 ======================

@router.get("/me", response_model=StandardResponse, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息（需登录）

    从 JWT Token 中解析用户身份
    """
    return StandardResponse(
        data=UserResponse.model_validate(current_user).model_dump(),
    )
