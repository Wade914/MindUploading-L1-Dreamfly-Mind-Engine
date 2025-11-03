"""
@Created on: 2025/01/15 10:00
@Author: DreamFly Team
@Des: DreamFly 意识上传平台 - 主入口文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.exception import http_error_handler, unicorn_exception_handler, UnicornException, http422_error_handler
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from core.path_manager import get_path_manager

# 导入路由
from api.endpoints.auth.view import router as auth_router
from api.endpoints.mind.view import router as mind_router
from api.endpoints.upload.view import router as upload_router
from api.endpoints.ai.view import router as ai_router
from api.endpoints.user_assets.view import router as user_assets_router
from api.endpoints.memory.view import router as memory_router
from api.endpoints.documents.view import router as documents_router
from api.endpoints.notes.view import router as notes_router
from api.endpoints.social.view import router as social_router
from api.endpoints.interaction.view import router as interaction_router
from api.endpoints.square.view import router as square_router

app = FastAPI(
    title="DreamFly API",
    description="DreamFly 数字意识上传平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(UnicornException, unicorn_exception_handler)
app.add_exception_handler(RequestValidationError, http422_error_handler)
app.add_exception_handler(ValidationError, http422_error_handler)

# 注册路由
app.include_router(auth_router, prefix="/api", tags=["认证"])
app.include_router(mind_router, prefix="/api", tags=["意识体"])
app.include_router(upload_router, prefix="/api", tags=["上传"])
app.include_router(ai_router, prefix="/api", tags=["AI服务"])
app.include_router(user_assets_router, tags=["用户资产管理"])
app.include_router(memory_router, tags=["记忆片段管理"])
app.include_router(documents_router, tags=["文档管理"])
app.include_router(notes_router, tags=["笔记管理"])
app.include_router(social_router, tags=["社交网络"])
app.include_router(interaction_router, prefix="/api", tags=["交互管理"])
app.include_router(square_router, tags=["广场"])

# 挂载静态文件目录
path_manager = get_path_manager()
app.mount("/uploads", StaticFiles(directory=str(path_manager.upload_dir)), name="uploads")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "DreamFly API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)