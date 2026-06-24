"""
FastAPI 应用主入口
负责组装中间件、路由和启动服务
"""
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router


# ====================== 应用生命周期 ======================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时：初始化数据库表结构
    - 关闭时：清理资源
    """
    # ======== 启动 ========
    print(f"[启动] {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    print(f"[数据库] {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")

    try:
        init_db()
        print("[数据库] 表结构初始化完成")
    except Exception as e:
        print(f"[警告] 数据库初始化失败: {e}")
        print("[提示] 请确保 MySQL 已启动且数据库已创建，或手动执行 init_db.sql")

    yield   # <<< 应用运行中 >>>

    # ======== 关闭 ========
    print("[关闭] 应用已安全停止")


# ====================== 创建应用 ======================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ====================== CORS 中间件 ======================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== 注册路由 ======================

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)


# ====================== 健康检查 ======================

@app.get("/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
    }

@app.get("/", tags=["系统"])
def root():
    """根路径"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
    }


# ====================== 直接运行 ======================

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
