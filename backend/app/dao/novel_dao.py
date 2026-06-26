"""
作品数据访问对象 (DAO)
封装 novels 表的 CRUD 操作
"""
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.novel import Novel


class NovelDAO:
    """
    作品数据访问对象
    """

    # ====================== 创建 ======================

    @staticmethod
    def create(db: Session, novel: Novel) -> Novel:
        """
        创建作品记录

        Args:
            db: 数据库会话
            novel: 作品模型实例

        Returns:
            Novel: 创建后的作品（含ID）
        """
        db.add(novel)
        db.commit()
        db.refresh(novel)
        return novel

    # ====================== 查询 ======================

    @staticmethod
    def get_by_id(db: Session, novel_id: int) -> Optional[Novel]:
        """
        根据自增ID查询作品

        Args:
            db: 数据库会话
            novel_id: 作品自增ID

        Returns:
            Optional[Novel]: 作品对象或 None
        """
        return db.query(Novel).filter(Novel.id == novel_id).first()

    @staticmethod
    def get_by_uuid(db: Session, novel_uuid: str) -> Optional[Novel]:
        """
        根据 UUID 查询作品

        Args:
            db: 数据库会话
            novel_uuid: 作品唯一UUID

        Returns:
            Optional[Novel]: 作品对象或 None
        """
        return db.query(Novel).filter(Novel.novel_uuid == novel_uuid).first()

    @staticmethod
    def get_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[Novel]:
        """
        查询作者的作品列表

        Args:
            db: 数据库会话
            author_id: 作者用户ID
            skip: 分页偏移
            limit: 分页大小

        Returns:
            List[Novel]: 作品列表
        """
        return (
            db.query(Novel)
            .filter(Novel.author_id == author_id)
            .order_by(desc(Novel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[Novel]:
        """
        查询所有作品列表（管理员用）

        Args:
            db: 数据库会话
            skip: 分页偏移
            limit: 分页大小

        Returns:
            List[Novel]: 作品列表
        """
        return (
            db.query(Novel)
            .order_by(desc(Novel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ====================== 更新 ======================

    @staticmethod
    def update(db: Session, novel: Novel) -> Novel:
        """
        更新作品记录

        Args:
            db: 数据库会话
            novel: 作品模型实例

        Returns:
            Novel: 更新后的作品
        """
        db.commit()
        db.refresh(novel)
        return novel

    @staticmethod
    def increment_likes(db: Session, novel_uuid: str, amount: int = 1) -> int:
        """
        递增点赞量

        Args:
            db: 数据库会话
            novel_uuid: 作品唯一UUID
            amount: 增量

        Returns:
            int: 更新后的点赞量
        """
        novel = db.query(Novel).filter(Novel.novel_uuid == novel_uuid).first()
        if novel:
            novel.likes = Novel.likes + amount
            db.commit()
            db.refresh(novel)
            return novel.likes
        return 0

    @staticmethod
    def increment_views(db: Session, novel_uuid: str, amount: int = 1) -> int:
        """
        递增观看量

        Args:
            db: 数据库会话
            novel_uuid: 作品唯一UUID
            amount: 增量

        Returns:
            int: 更新后的观看量
        """
        novel = db.query(Novel).filter(Novel.novel_uuid == novel_uuid).first()
        if novel:
            novel.views = Novel.views + amount
            db.commit()
            db.refresh(novel)
            return novel.views
        return 0

    @staticmethod
    def increment_comments(db: Session, novel_uuid: str, amount: int = 1) -> int:
        """
        递增评论量

        Args:
            db: 数据库会话
            novel_uuid: 作品唯一UUID
            amount: 增量

        Returns:
            int: 更新后的评论量
        """
        novel = db.query(Novel).filter(Novel.novel_uuid == novel_uuid).first()
        if novel:
            novel.comments = Novel.comments + amount
            db.commit()
            db.refresh(novel)
            return novel.comments
        return 0

    # ====================== 删除 ======================

    @staticmethod
    def delete(db: Session, novel: Novel) -> bool:
        """
        删除作品记录

        Args:
            db: 数据库会话
            novel: 作品模型实例

        Returns:
            bool: 是否删除成功
        """
        db.delete(novel)
        db.commit()
        return True

    @staticmethod
    def delete_by_uuid(db: Session, novel_uuid: str) -> bool:
        """
        根据 UUID 删除作品

        Args:
            db: 数据库会话
            novel_uuid: 作品唯一UUID

        Returns:
            bool: 是否删除成功
        """
        novel = db.query(Novel).filter(Novel.novel_uuid == novel_uuid).first()
        if novel:
            db.delete(novel)
            db.commit()
            return True
        return False
