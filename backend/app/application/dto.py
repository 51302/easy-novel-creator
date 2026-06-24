"""
数据传输对象 (Data Transfer Object)
定义接口层请求/响应的数据结构（Pydantic Schema）
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


# ====================== 请求 Schema ======================

class LoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    email:    Optional[str] = Field(None, max_length=100, description="邮箱")
    phone:    Optional[str] = Field(None, max_length=20, description="手机号")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """校验用户名只包含字母数字下划线"""
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v.strip()


class UpdateUserRequest(BaseModel):
    """更新用户信息请求（管理员使用）"""
    email:      Optional[str] = Field(None, max_length=100)
    phone:      Optional[str] = Field(None, max_length=20)
    status:     Optional[int] = Field(None, ge=0, le=1)
    superuser:  Optional[int] = Field(None, ge=0, le=1)


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")


# ====================== 响应 Schema ======================

class UserResponse(BaseModel):
    """用户信息响应（不含敏感字段）"""
    id:         int
    username:   str
    status:     int
    email:      Optional[str] = None
    phone:      Optional[str] = None
    superuser:  int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录成功响应"""
    access_token: str  = Field(..., description="JWT 访问令牌")
    token_type:   str  = Field(default="bearer", description="令牌类型")
    user:         UserResponse


class TokenPayload(BaseModel):
    """JWT Token 解析后的载荷"""
    sub:   str = Field(..., description="用户名 (subject)")
    user_id: int = Field(..., description="用户ID")
    superuser: int = Field(default=0, description="是否超级管理员")


class PaginatedResponse(BaseModel):
    """分页响应"""
    total:   int
    page:    int
    size:    int
    items:   list[UserResponse]


class StandardResponse(BaseModel):
    """统一 API 响应格式"""
    code:    int    = Field(default=200, description="业务状态码")
    message: str   = Field(default="success", description="响应消息")
    data:    Optional[dict | list] = Field(default=None, description="响应数据")
