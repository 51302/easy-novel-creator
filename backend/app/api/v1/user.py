"""
用户管理接口模块
提供管理员用户管理和个人信息查询 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.service.user_service import UserService
from app.application.dto import (
    UpdateUserRequest, StandardResponse, PaginatedResponse,
)

router = APIRouter(prefix="/users", tags=["用户管理"])


# ====================== 获取用户列表（管理员） ======================

@router.get("", response_model=StandardResponse, summary="获取用户列表")
def list_users(
    page:   int = Query(default=1, ge=1, description="页码"),
    size:   int = Query(default=20, ge=1, le=100, description="每页数量"),
    status: int = Query(default=None, ge=0, le=1, description="状态筛选"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """
    获取用户列表（需超级管理员权限）

    支持分页和按状态筛选
    """
    users, total = UserService.list_users(db, page=page, size=size, status=status)

    return StandardResponse(
        data={
            "total": total,
            "page": page,
            "size": size,
            "items": [u.model_dump() for u in users],
        },
    )


# ====================== 获取单个用户 ======================

@router.get("/{user_id}", response_model=StandardResponse, summary="获取用户详情")
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取指定用户的详细信息（需登录）
    """
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return StandardResponse(data=user.model_dump())


# ====================== 更新用户信息（管理员） ======================

@router.put("/{user_id}", response_model=StandardResponse, summary="更新用户信息")
def update_user(
    user_id: int,
    req: UpdateUserRequest,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """
    管理员更新用户信息（需超级管理员权限）

    支持部分更新：只传需要修改的字段即可
    """
    from app.dao.user_dao import UserDAO

    target = UserDAO.get_by_id(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    user, error = UserService.update_user_by_admin(db, target, req)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(
        message="更新成功",
        data=user.model_dump(),
    )


# ====================== 删除用户（管理员） ======================

@router.delete("/{user_id}", response_model=StandardResponse, summary="删除用户")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """
    管理员删除用户（需超级管理员权限）
    """
    from app.dao.user_dao import UserDAO

    # 不允许删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号",
        )

    target = UserDAO.get_by_id(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    UserService.delete_user(db, target)
    return StandardResponse(message="删除成功")
