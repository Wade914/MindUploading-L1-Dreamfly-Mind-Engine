# DreamFly Python Backend

DreamFly 数字意识上传平台的 Python 后端实现，基于 FastAPI 框架。

## 功能特性

- 🔐 **用户认证**: 用户注册、登录功能
- 🧠 **意识体管理**: 创建、查询、管理数字意识体
- 📁 **文件上传**: 支持思想、声音、形象数据上传
- 🗄️ **数据存储**: SQLite 数据库 + 文件存储
- 📚 **API文档**: 自动生成的 Swagger/OpenAPI 文档
- 🚀 **异步支持**: 基于 FastAPI 的高性能异步处理

## 技术栈

- **Web框架**: FastAPI 0.104.1
- **数据库**: SQLite + SQLAlchemy 2.0 (异步)
- **数据验证**: Pydantic 2.5
- **服务器**: Uvicorn
- **文件处理**: Python-multipart

## 项目结构

```
pybackend/
├── api/                    # API模块
│   └── endpoints/         # 端点定义
│       ├── auth/          # 用户认证模块
│       │   ├── models.py  # 数据模型
│       │   ├── params.py  # 请求参数
│       │   ├── schemas.py # 响应模式
│       │   ├── service.py # 业务逻辑
│       │   └── view.py    # API视图
│       ├── mind/          # 意识体管理模块
│       └── upload/        # 文件上传模块
├── cfg/                   # 配置模块
│   └── config.py         # 项目配置
├── core/                  # 核心模块
│   ├── crud.py           # 基础CRUD操作
│   ├── exception.py      # 异常处理
│   ├── response.py       # 响应格式
│   └── utils.py          # 工具函数
├── database/              # 数据库模块
│   ├── models.py         # 数据模型
│   └── session.py        # 数据库会话
├── main.py               # 应用入口
├── init_db.py            # 数据库初始化
├── start.py              # 启动脚本
└── requirements.txt      # 依赖包
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python start.py
```

或者手动启动：

```bash
# 初始化数据库
python init_db.py

# 启动服务器
python main.py
```

### 3. 访问文档

- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## API接口

### 用户认证 (/api)

- `POST /register` - 用户注册
- `POST /login` - 用户登录

### 意识体管理 (/api)

- `POST /mind` - 创建意识体
- `GET /minds` - 获取意识体列表（分页）
- `GET /mind-list` - 获取意识体文件名列表
- `GET /mind/{filename}` - 获取指定意识体内容

### 文件上传 (/api)

- `POST /upload` - 上传文件
- `GET /uploads` - 获取上传列表
- `DELETE /upload/{file_id}` - 删除文件

## 配置说明

项目配置文件位于 `cfg/config.py`，支持环境变量配置。

复制 `.env.example` 为 `.env` 并修改相应配置：

```bash
cp .env.example .env
```

### 主要配置项

- `DATABASE_URL`: 数据库连接字符串
- `UPLOAD_DIR`: 文件上传目录
- `MAX_FILE_SIZE`: 最大文件大小限制
- `MINDS_DIR`: 意识体数据目录

## 文件上传限制

- **思想数据**: 5MB (.txt, .md, .doc, .docx, .pdf)
- **声音数据**: 10MB (.mp3, .wav, .m4a, .aac)
- **形象数据**: 20MB (.jpg, .jpeg, .png, .gif, .bmp)

## 开发指南

### 添加新的API模块

1. 在 `api/endpoints/` 下创建新目录
2. 创建以下文件：
   - `models.py`: 数据模型
   - `params.py`: 请求参数
   - `schemas.py`: 响应模式
   - `service.py`: 业务逻辑
   - `view.py`: API视图
3. 在 `main.py` 中注册路由

### 数据库迁移

当修改数据模型后，需要重新初始化数据库：

```bash
python init_db.py
```

## 部署说明

### 生产环境部署

1. 设置环境变量 `DEBUG=false`
2. 配置生产数据库（如 PostgreSQL）
3. 使用 Gunicorn 或其他 WSGI 服务器
4. 配置反向代理（如 Nginx）

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start.py"]
```

## 许可证

该项目遵循 MIT 许可证。