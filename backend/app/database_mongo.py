"""
MongoDB 连接管理模块
使用 pymongo 管理 MongoDB 数据库连接
存储作品的详细内容信息（简介、世界设定、故事背景等）
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from app.config import settings


# ====================== MongoDB 客户端 ======================
_mongo_client: MongoClient | None = None
_mongo_db: Database | None = None


def get_mongo_client() -> MongoClient:
    """
    获取 MongoDB 客户端实例（单例）

    Returns:
        MongoClient: MongoDB 客户端
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(
            settings.MONGO_URI,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
    return _mongo_client


def get_mongo_db() -> Database:
    """
    获取 MongoDB 数据库实例

    Returns:
        Database: MongoDB 数据库对象
    """
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[settings.MONGO_DATABASE]
    return _mongo_db


def get_novel_collection() -> Collection:
    """
    获取作品详细内容集合 (novels_detail)

    Returns:
        Collection: novels_detail 集合
    """
    db = get_mongo_db()
    return db["novels_detail"]


def init_mongo_indexes():
    """
    初始化 MongoDB 索引
    在应用启动时调用，确保查询性能
    """
    collection = get_novel_collection()
    # 为 novel_uuid 创建唯一索引
    collection.create_index("novel_uuid", unique=True, name="idx_novel_uuid")
    # 为 author_id 创建索引（查询作者的所有作品）
    collection.create_index("author_id", name="idx_author_id")
    # 为 title 创建文本索引（支持全文搜索）
    collection.create_index([("title", "text"), ("synopsis", "text")], name="idx_text_search")
    print("[MongoDB] 索引初始化完成")


def close_mongo_client():
    """
    关闭 MongoDB 客户端连接
    在应用关闭时调用
    """
    global _mongo_client, _mongo_db
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        print("[MongoDB] 连接已关闭")
