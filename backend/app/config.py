"""
应用配置模块
管理数据库连接、JWT密钥等配置项
"""
import os
from typing import Optional
import yaml


def load_yaml_config():
    """加载 YAML 配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), "conf", "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return None


yaml_config = load_yaml_config()


class Settings:
    """应用全局配置"""

    def __init__(self):
        # 从 YAML 配置加载，优先使用环境变量覆盖
        self._load_from_yaml()

    def _load_from_yaml(self):
        """从 YAML 文件加载配置"""
        if yaml_config:
            # MySQL 配置
            mysql_config = yaml_config.get('mysql', {})
            self.MYSQL_HOST = os.getenv("MYSQL_HOST", mysql_config.get('host', '127.0.0.1'))
            self.MYSQL_PORT = int(os.getenv("MYSQL_PORT", mysql_config.get('port', 3306)))
            self.MYSQL_USER = os.getenv("MYSQL_USER", mysql_config.get('user', 'root'))
            self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", mysql_config.get('password', 'root'))
            self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", mysql_config.get('database', 'auth_system'))

            # MongoDB 配置
            mongo_config = yaml_config.get('mongodb', {})
            mongo_host = os.getenv("MONGO_HOST", mongo_config.get('host', '127.0.0.1'))
            mongo_port = int(os.getenv("MONGO_PORT", mongo_config.get('port', 27017)))
            mongo_user = os.getenv("MONGO_USER", mongo_config.get('user', 'admin'))
            mongo_password = os.getenv("MONGO_PASSWORD", mongo_config.get('password', 'admin123'))
            self.MONGO_DATABASE = os.getenv("MONGO_DATABASE", mongo_config.get('database', 'novel_db'))
            self.MONGO_URI = os.getenv(
                "MONGO_URI",
                mongo_config.get('uri', f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{self.MONGO_DATABASE}?authSource=admin")
            )

            # Redis 配置
            redis_config = yaml_config.get('redis', {})
            self.REDIS_HOST = os.getenv("REDIS_HOST", redis_config.get('host', '127.0.0.1'))
            self.REDIS_PORT = int(os.getenv("REDIS_PORT", redis_config.get('port', 6379)))
            self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", redis_config.get('password', 'novel123redis'))
            self.REDIS_DB = int(os.getenv("REDIS_DB", redis_config.get('db', 0)))

            # 应用配置
            app_config = yaml_config.get('app', {})
            self.PROJECT_NAME = app_config.get('name', 'Auth System')
            self.PROJECT_VERSION = app_config.get('version', '1.0.0')
            self.PROJECT_DESCRIPTION = "用户认证与管理系统"
            self.API_V1_PREFIX = "/api/v1"
            self.DEBUG = os.getenv("DEBUG", str(app_config.get('debug', True))).lower() == "true"

            server_config = app_config.get('server', {})
            self.HOST = os.getenv("HOST", server_config.get('host', '0.0.0.0'))
            self.PORT = int(os.getenv("PORT", server_config.get('port', 8000)))

            # JWT 配置
            jwt_config = yaml_config.get('jwt', {})
            self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", jwt_config.get('secret_key', 'your-secret-key-change-in-production-2024'))
            self.JWT_ALGORITHM = jwt_config.get('algorithm', 'HS256')
            self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", jwt_config.get('access_token_expire_minutes', 60)))

            # CORS 配置
            cors_config = yaml_config.get('cors', {})
            self.CORS_ORIGINS = cors_config.get('origins', ["http://localhost:3000", "http://127.0.0.1:3000"])

            # 密码加密配置
            self.PASSWORD_HASH_ROUNDS = 12
        else:
            # 默认配置（当 YAML 文件不存在时）
            self._load_defaults()

    def _load_defaults(self):
        """加载默认配置"""
        self.PROJECT_NAME = "AI Novel Creator"
        self.PROJECT_VERSION = "1.0.0"
        self.PROJECT_DESCRIPTION = "AI小说创作平台"
        self.API_V1_PREFIX = "/api/v1"
        self.MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        self.MYSQL_USER = os.getenv("MYSQL_USER", "root")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
        self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "auth_system")
        # MongoDB 默认配置
        mongo_host = os.getenv("MONGO_HOST", "127.0.0.1")
        mongo_port = int(os.getenv("MONGO_PORT", "27017"))
        mongo_user = os.getenv("MONGO_USER", "admin")
        mongo_password = os.getenv("MONGO_PASSWORD", "admin123")
        self.MONGO_DATABASE = os.getenv("MONGO_DATABASE", "novel_db")
        self.MONGO_URI = os.getenv("MONGO_URI", f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{self.MONGO_DATABASE}?authSource=admin")
        # Redis 默认配置
        self.REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "novel123redis")
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2024")
        self.JWT_ALGORITHM = "HS256"
        self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.PASSWORD_HASH_ROUNDS = 12
        self.CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        """动态构建数据库连接URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            "?charset=utf8mb4"
        )

    # 同步引擎的备用URL（不含async前缀驱动）
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL


settings = Settings()
