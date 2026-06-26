"""
作品服务模块
包含作品创建、查询、修改、删除等核心业务逻辑
协调 MySQL（元数据/统计）、MongoDB（详情内容）、Redis（缓存）三层存储
"""
import json
import uuid
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from app.dao.novel_dao import NovelDAO
from app.models.novel import Novel
from app.models.user import User
from app.database_mongo import get_novel_collection
from app.database_redis import RedisCache


class NovelService:
    """
    作品服务层
    封装作品相关的所有业务逻辑
    """

    # ====================== 作品创建 ======================

    @staticmethod
    def create_novel(
        db: Session,
        current_user: User,
        title: str,
        synopsis: str,
        novel_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        story_background: Optional[str] = None,
        world_building: Optional[str] = None,
        characters: Optional[List[dict]] = None,
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        创建作品
        流程:
            1. MySQL 保存作品元数据和统计信息
            2. MongoDB 保存作品详细内容（简介、世界设定、故事背景等）
            3. Redis 预热缓存（清空该作者的作品列表缓存）

        Args:
            db: 数据库会话
            current_user: 当前登录用户
            title: 作品名称
            synopsis: 作品简介
            novel_type: 作品类型/目标读者
            tags: 标签列表
            story_background: 故事背景
            world_building: 世界设定
            characters: 角色列表 [{name, description}]

        Returns:
            (dict, None) 创建成功，返回作品概要
            (None, "错误信息") 创建失败
        """
        try:
            # 1. 在 MySQL 中创建作品元数据
            novel_uuid = str(uuid.uuid4())
            novel = Novel(
                novel_uuid=novel_uuid,
                author_id=current_user.id,
                author_name=current_user.username,
                title=title,
                novel_type=novel_type,
                tags=json.dumps(tags, ensure_ascii=False) if tags else None,
                likes=0,
                views=0,
                comments=0,
            )
            novel = NovelDAO.create(db, novel)

            # 2. 在 MongoDB 中保存作品详细内容
            mongo_collection = get_novel_collection()
            mongo_doc = {
                "novel_uuid": novel_uuid,
                "author_id": current_user.id,
                "author_name": current_user.username,
                "title": title,
                "synopsis": synopsis,
                "world_building": world_building or "",
                "story_background": story_background or "",
                "characters": characters or [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            mongo_collection.insert_one(mongo_doc)

            # 3. 清空该作者的作品列表缓存（使缓存失效）
            RedisCache.delete_novel_list(f"author:{current_user.id}")

            # 4. 构建响应数据
            result = {
                "id": novel.id,
                "novel_uuid": novel.novel_uuid,
                "title": novel.title,
                "author_id": novel.author_id,
                "author_name": novel.author_name,
                "novel_type": novel.novel_type,
                "tags": tags or [],
                "likes": novel.likes,
                "views": novel.views,
                "comments": novel.comments,
                "created_at": novel.created_at.isoformat() if novel.created_at else None,
            }
            return result, None

        except Exception as e:
            return None, f"创建作品失败: {str(e)}"

    # ====================== 作品查询 ======================

    @staticmethod
    def get_my_novels(db: Session, current_user: User) -> Tuple[List[dict], Optional[str]]:
        """
        获取当前用户的作品列表
        流程:
            1. 先查 Redis 缓存
            2. 未命中则查 MySQL
            3. 写入 Redis 缓存

        Args:
            db: 数据库会话
            current_user: 当前登录用户

        Returns:
            (List[dict], None) 查询成功
            ([], "错误信息") 查询失败
        """
        cache_key = f"author:{current_user.id}"

        # 1. 尝试从 Redis 缓存获取
        cached = RedisCache.get_novel_list(cache_key)
        if cached is not None:
            return cached, None

        try:
            # 2. 从 MySQL 查询
            novels = NovelDAO.get_by_author(db, current_user.id, limit=100)

            result = []
            for novel in novels:
                tags = []
                if novel.tags:
                    try:
                        tags = json.loads(novel.tags)
                    except Exception:
                        tags = []
                result.append({
                    "id": novel.id,
                    "novel_uuid": novel.novel_uuid,
                    "title": novel.title,
                    "novel_type": novel.novel_type,
                    "tags": tags,
                    "likes": novel.likes,
                    "views": novel.views,
                    "comments": novel.comments,
                    "created_at": novel.created_at.isoformat() if novel.created_at else None,
                })

            # 3. 写入 Redis 缓存（5分钟）
            RedisCache.set_novel_list(cache_key, result, expire=300)

            return result, None

        except Exception as e:
            return [], f"查询作品列表失败: {str(e)}"

    @staticmethod
    def get_novel_for_edit(db: Session, current_user: User, novel_uuid: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        获取作品完整详情（用于编辑）
        聚合 MySQL 元数据 + MongoDB 详细内容

        Args:
            db: 数据库会话
            current_user: 当前登录用户
            novel_uuid: 作品唯一UUID

        Returns:
            (dict, None) 查询成功
            (None, "错误信息") 查询失败
        """
        try:
            # 1. 从 MySQL 查询作品元数据
            novel = NovelDAO.get_by_uuid(db, novel_uuid)
            if not novel:
                return None, "作品不存在"

            # 权限校验：只能编辑自己的作品（管理员除外）
            if novel.author_id != current_user.id and not current_user.superuser:
                return None, "无权查看该作品"

            # 2. 从 MongoDB 查询详细内容
            mongo_collection = get_novel_collection()
            mongo_doc = mongo_collection.find_one({"novel_uuid": novel_uuid})

            # 3. 组装完整数据
            tags = []
            if novel.tags:
                try:
                    tags = json.loads(novel.tags)
                except Exception:
                    tags = []

            result = {
                "id": novel.id,
                "novel_uuid": novel.novel_uuid,
                "author_id": novel.author_id,
                "author_name": novel.author_name,
                "title": novel.title,
                "novel_type": novel.novel_type,
                "tags": tags,
                "likes": novel.likes,
                "views": novel.views,
                "comments": novel.comments,
                "created_at": novel.created_at.isoformat() if novel.created_at else None,
                "updated_at": novel.updated_at.isoformat() if novel.updated_at else None,
                # MongoDB 详细内容
                "synopsis": mongo_doc.get("synopsis", "") if mongo_doc else "",
                "world_building": mongo_doc.get("world_building", "") if mongo_doc else "",
                "story_background": mongo_doc.get("story_background", "") if mongo_doc else "",
                "characters": mongo_doc.get("characters", []) if mongo_doc else [],
            }

            return result, None

        except Exception as e:
            return None, f"查询作品失败: {str(e)}"

    # ====================== 作品修改 ======================

    @staticmethod
    def update_novel(
        db: Session,
        current_user: User,
        novel_uuid: str,
        title: Optional[str] = None,
        synopsis: Optional[str] = None,
        novel_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        story_background: Optional[str] = None,
        world_building: Optional[str] = None,
        characters: Optional[List[dict]] = None,
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        修改作品
        流程:
            1. MySQL 更新作品元数据（只更新传入的字段）
            2. MongoDB 更新作品详细内容（只更新传入的字段）
            3. Redis 清空相关缓存

        Args:
            db: 数据库会话
            current_user: 当前登录用户
            novel_uuid: 作品唯一UUID
            title: 作品名称（可选）
            synopsis: 作品简介（可选）
            novel_type: 作品类型（可选）
            tags: 标签列表（可选）
            story_background: 故事背景（可选）
            world_building: 世界设定（可选）
            characters: 角色列表（可选）

        Returns:
            (dict, None) 修改成功
            (None, "错误信息") 修改失败
        """
        try:
            # 1. 查询作品
            novel = NovelDAO.get_by_uuid(db, novel_uuid)
            if not novel:
                return None, "作品不存在"

            # 权限校验：只能修改自己的作品（管理员除外）
            if novel.author_id != current_user.id and not current_user.superuser:
                return None, "无权修改该作品"

            # 2. 更新 MySQL 字段（只更新传入的值）
            if title is not None:
                novel.title = title
            if novel_type is not None:
                novel.novel_type = novel_type
            if tags is not None:
                novel.tags = json.dumps(tags, ensure_ascii=False) if tags else None
            db.commit()
            db.refresh(novel)

            # 3. 更新 MongoDB 字段（只更新传入的值）
            mongo_collection = get_novel_collection()
            update_doc = {"updated_at": datetime.utcnow()}

            if synopsis is not None:
                update_doc["synopsis"] = synopsis
            if world_building is not None:
                update_doc["world_building"] = world_building
            if story_background is not None:
                update_doc["story_background"] = story_background
            if characters is not None:
                update_doc["characters"] = characters
            if title is not None:
                update_doc["title"] = title

            if len(update_doc) > 1:  # 有除了 updated_at 之外的字段需要更新
                mongo_collection.update_one(
                    {"novel_uuid": novel_uuid},
                    {"$set": update_doc}
                )

            # 4. 清空 Redis 缓存
            RedisCache.delete_novel_detail(novel_uuid)
            RedisCache.delete_stats(novel_uuid)
            RedisCache.delete_novel_list(f"author:{novel.author_id}")

            # 5. 构建响应数据
            result_tags = []
            if novel.tags:
                try:
                    result_tags = json.loads(novel.tags)
                except Exception:
                    result_tags = []

            result = {
                "id": novel.id,
                "novel_uuid": novel.novel_uuid,
                "title": novel.title,
                "author_id": novel.author_id,
                "author_name": novel.author_name,
                "novel_type": novel.novel_type,
                "tags": result_tags,
                "likes": novel.likes,
                "views": novel.views,
                "comments": novel.comments,
                "created_at": novel.created_at.isoformat() if novel.created_at else None,
                "updated_at": novel.updated_at.isoformat() if novel.updated_at else None,
            }
            return result, None

        except Exception as e:
            return None, f"修改作品失败: {str(e)}"

    # ====================== 作品删除 ======================

    @staticmethod
    def delete_novel(db: Session, current_user: User, novel_uuid: str) -> Tuple[bool, Optional[str]]:
        """
        删除作品
        流程:
            1. 删除 MySQL 记录
            2. 删除 MongoDB 记录
            3. 删除 Redis 缓存

        Args:
            db: 数据库会话
            current_user: 当前登录用户
            novel_uuid: 作品唯一UUID

        Returns:
            (True, None) 删除成功
            (False, "错误信息") 删除失败
        """
        try:
            # 查询作品
            novel = NovelDAO.get_by_uuid(db, novel_uuid)
            if not novel:
                return False, "作品不存在"

            # 权限校验：只能删除自己的作品（管理员除外）
            if novel.author_id != current_user.id and not current_user.superuser:
                return False, "无权删除该作品"

            # 1. 删除 MySQL 记录
            NovelDAO.delete(db, novel)

            # 2. 删除 MongoDB 记录
            mongo_collection = get_novel_collection()
            mongo_collection.delete_one({"novel_uuid": novel_uuid})

            # 3. 删除 Redis 缓存
            RedisCache.delete_novel_detail(novel_uuid)
            RedisCache.delete_stats(novel_uuid)
            RedisCache.delete_novel_list(f"author:{novel.author_id}")

            return True, None

        except Exception as e:
            return False, f"删除作品失败: {str(e)}"
