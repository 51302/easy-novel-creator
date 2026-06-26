"""
Redis 连接管理模块
使用 redis-py 管理 Redis 缓存连接
用于作品列表缓存、点赞量/观看量/评论量的高速读写、热点数据缓存
"""
import json
from typing import Any, Optional

import redis

from app.config import settings


# ====================== Redis 客户端 ======================
_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """
    获取 Redis 客户端实例（单例）

    Returns:
        redis.Redis: Redis 客户端
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,          # 自动解码为字符串
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
        )
    return _redis_client


def close_redis_client():
    """
    关闭 Redis 客户端连接
    在应用关闭时调用
    """
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        print("[Redis] 连接已关闭")


# ====================== 缓存工具函数 ======================

class RedisCache:
    """
    Redis 缓存封装类
    提供作品相关的缓存操作方法
    """

    # 缓存键前缀
    PREFIX_NOVEL = "novel"
    PREFIX_NOVEL_LIST = "novel:list"
    PREFIX_NOVEL_STATS = "novel:stats"

    @staticmethod
    def _key(prefix: str, *parts: str) -> str:
        """构建缓存键"""
        return ":".join([prefix] + list(parts))

    # ------------------ 作品详情缓存 ------------------

    @staticmethod
    def get_novel_detail(novel_uuid: str) -> Optional[dict]:
        """
        获取作品详情缓存

        Args:
            novel_uuid: 作品唯一UUID

        Returns:
            Optional[dict]: 缓存的作品详情，未命中返回 None
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL, novel_uuid)
            data = client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    @staticmethod
    def set_novel_detail(novel_uuid: str, data: dict, expire: int = 3600):
        """
        设置作品详情缓存

        Args:
            novel_uuid: 作品唯一UUID
            data: 作品详情数据
            expire: 过期时间（秒），默认1小时
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL, novel_uuid)
            client.setex(key, expire, json.dumps(data, ensure_ascii=False, default=str))
        except Exception:
            pass

    @staticmethod
    def delete_novel_detail(novel_uuid: str):
        """删除作品详情缓存"""
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL, novel_uuid)
            client.delete(key)
        except Exception:
            pass

    # ------------------ 作品统计缓存 (点赞/观看/评论) ------------------

    @staticmethod
    def increment_stat(novel_uuid: str, stat_type: str, amount: int = 1) -> int:
        """
        原子递增作品统计量

        Args:
            novel_uuid: 作品唯一UUID
            stat_type: 统计类型 (likes, views, comments)
            amount: 增量

        Returns:
            int: 递增后的值
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_STATS, novel_uuid)
            return client.hincrby(key, stat_type, amount)
        except Exception:
            return 0

    @staticmethod
    def get_stats(novel_uuid: str) -> dict:
        """
        获取作品统计量

        Args:
            novel_uuid: 作品唯一UUID

        Returns:
            dict: {likes, views, comments}
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_STATS, novel_uuid)
            stats = client.hgetall(key)
            return {
                "likes": int(stats.get("likes", 0)),
                "views": int(stats.get("views", 0)),
                "comments": int(stats.get("comments", 0)),
            }
        except Exception:
            return {"likes": 0, "views": 0, "comments": 0}

    @staticmethod
    def set_stats(novel_uuid: str, likes: int = 0, views: int = 0, comments: int = 0, expire: int = 7200):
        """
        设置作品统计量缓存

        Args:
            novel_uuid: 作品唯一UUID
            likes: 点赞量
            views: 观看量
            comments: 评论量
            expire: 过期时间（秒），默认2小时
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_STATS, novel_uuid)
            client.hset(key, mapping={
                "likes": likes,
                "views": views,
                "comments": comments,
            })
            client.expire(key, expire)
        except Exception:
            pass

    @staticmethod
    def delete_stats(novel_uuid: str):
        """删除作品统计缓存"""
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_STATS, novel_uuid)
            client.delete(key)
        except Exception:
            pass

    # ------------------ 作品列表缓存 ------------------

    @staticmethod
    def get_novel_list(cache_key: str) -> Optional[list]:
        """
        获取作品列表缓存

        Args:
            cache_key: 列表缓存键（如 'my_novels:user_id:1'）

        Returns:
            Optional[list]: 缓存的列表数据
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_LIST, cache_key)
            data = client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    @staticmethod
    def set_novel_list(cache_key: str, data: list, expire: int = 300):
        """
        设置作品列表缓存

        Args:
            cache_key: 列表缓存键
            data: 列表数据
            expire: 过期时间（秒），默认5分钟
        """
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_LIST, cache_key)
            client.setex(key, expire, json.dumps(data, ensure_ascii=False, default=str))
        except Exception:
            pass

    @staticmethod
    def delete_novel_list(cache_key: str):
        """删除作品列表缓存"""
        try:
            client = get_redis_client()
            key = RedisCache._key(RedisCache.PREFIX_NOVEL_LIST, cache_key)
            client.delete(key)
        except Exception:
            pass

    @staticmethod
    def clear_all_novel_lists():
        """清空所有作品列表缓存"""
        try:
            client = get_redis_client()
            pattern = RedisCache._key(RedisCache.PREFIX_NOVEL_LIST, "*")
            for key in client.scan_iter(match=pattern):
                client.delete(key)
        except Exception:
            pass
