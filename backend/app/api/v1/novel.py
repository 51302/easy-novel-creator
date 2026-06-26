"""
作品接口模块
提供作品创建、查询、修改、删除等 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.service.novel_service import NovelService
from app.application.dto import (
    CreateNovelRequest,
    UpdateNovelRequest,
    StandardResponse,
)

router = APIRouter(prefix="/novels", tags=["作品"])


# ====================== 创建作品 ======================

@router.post("/create", response_model=StandardResponse, summary="创建作品")
def create_novel(
    req: CreateNovelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新作品

    数据流向:
        - MySQL: 保存作品元数据（id, uuid, 作者, 书名, 类型, 标签, 统计量, 时间戳）
        - MongoDB: 保存作品详细内容（简介, 世界设定, 故事背景, 角色）
        - Redis: 清空该作者的作品列表缓存

    请求字段:
        - **title**: 作品名称（必填，1-100字符）
        - **synopsis**: 作品简介（必填，1-2000字符）
        - **novel_type**: 作品类型/目标读者（可选，male=男频, female=女频）
        - **tags**: 标签列表（可选，如 ["玄幻", "热血"]）
        - **story_background**: 故事背景（可选）
        - **world_building**: 世界设定（可选）
        - **characters**: 角色列表（可选，[{name, description}]）
    """
    data, error = NovelService.create_novel(
        db=db,
        current_user=current_user,
        title=req.title,
        synopsis=req.synopsis,
        novel_type=req.novel_type,
        tags=req.tags,
        story_background=req.story_background,
        world_building=req.world_building,
        characters=[c.model_dump() for c in req.characters] if req.characters else [],
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(
        code=201,
        message="作品创建成功",
        data=data,
    )


# ====================== 查询作品列表 ======================

@router.get("/", response_model=StandardResponse, summary="获取我的作品列表")
def list_my_novels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取当前登录用户的作品列表

    使用 Redis 缓存加速，缓存有效期 5 分钟
    """
    data, error = NovelService.get_my_novels(db, current_user)
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(
        code=200,
        message="查询成功",
        data={"items": data, "total": len(data)},
    )


# ====================== 获取作品详情（用于编辑） ======================

@router.get("/{novel_uuid}/edit", response_model=StandardResponse, summary="获取作品详情（编辑用）")
def get_novel_for_edit(
    novel_uuid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取作品完整详情（用于编辑页面）

    聚合 MySQL 元数据 + MongoDB 详细内容，返回完整的作品信息供前端填充表单
    只能获取自己的作品（管理员除外）

    - **novel_uuid**: 作品唯一UUID
    """
    data, error = NovelService.get_novel_for_edit(db, current_user, novel_uuid)
    if error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error,
        )
    return StandardResponse(
        code=200,
        message="查询成功",
        data=data,
    )


# ====================== 修改作品 ======================

@router.put("/{novel_uuid}", response_model=StandardResponse, summary="修改作品")
def update_novel(
    novel_uuid: str,
    req: UpdateNovelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    修改已有作品

    数据流向:
        - MySQL: 更新作品元数据（书名, 类型, 标签）
        - MongoDB: 更新作品详细内容（简介, 世界设定, 故事背景, 角色）
        - Redis: 清空该作品的详情缓存和作者列表缓存

    只能修改自己的作品（管理员除外）

    请求字段（均为可选，不传则不修改）:
        - **title**: 作品名称
        - **synopsis**: 作品简介
        - **novel_type**: 作品类型（male=男频, female=女频）
        - **tags**: 标签列表
        - **story_background**: 故事背景
        - **world_building**: 世界设定
        - **characters**: 角色列表
    """
    data, error = NovelService.update_novel(
        db=db,
        current_user=current_user,
        novel_uuid=novel_uuid,
        title=req.title,
        synopsis=req.synopsis,
        novel_type=req.novel_type,
        tags=req.tags,
        story_background=req.story_background,
        world_building=req.world_building,
        characters=[c.model_dump() for c in req.characters] if req.characters else None,
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(
        code=200,
        message="作品修改成功",
        data=data,
    )


# ====================== 删除作品 ======================

@router.delete("/{novel_uuid}", response_model=StandardResponse, summary="删除作品")
def delete_novel(
    novel_uuid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除作品

    同时删除 MySQL、MongoDB 中的数据，并清空 Redis 缓存
    只能删除自己的作品（管理员除外）
    """
    success, error = NovelService.delete_novel(db, current_user, novel_uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return StandardResponse(
        code=200,
        message="删除成功",
    )
