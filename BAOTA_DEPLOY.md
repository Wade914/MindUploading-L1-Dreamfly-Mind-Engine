# DreamFly 宝塔面板部署指南

## 📋 部署概述

本指南将帮你在宝塔面板上部署 DreamFly 项目，包括前端和后端的完整部署流程。

## 🛠️ 环境要求

### 服务器配置
- **操作系统**: CentOS 7+ / Ubuntu 18+ / Debian 9+
- **内存**: 2GB+ (推荐4GB+)
- **硬盘**: 20GB+ 可用空间
- **网络**: 公网IP，开放80、443、8000端口

### 宝塔面板版本
- **宝塔Linux面板**: 7.7.0+
- **必装软件**: Nginx、Python 3.8+、Node.js 16+、PM2

## 🚀 部署步骤

### 第一步：安装宝塔面板

```bash
# CentOS安装命令
yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh

# Ubuntu/Debian安装命令
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
```

### 第二步：安装必要软件

在宝塔面板 → 软件商店 → 安装以下软件：
1. **Nginx** (1.20+)
2. **Python项目管理器** (用于管理Python环境)
3. **Node.js版本管理器** (安装Node.js 16+)
4. **PM2管理器** (用于进程管理)

### 第三步：上传项目文件

1. 在宝塔面板 → 文件 → 创建网站目录
   ```
   /www/wwwroot/dreamfly/
   ```

2. 上传项目文件到服务器
   ```
   /www/wwwroot/dreamfly/
   ├── pybackend/          # 后端代码
   ├── src/               # 前端源码
   ├── package.json       # 前端依赖
   ├── .env              # 环境配置
   └── ...
   ```

### 第四步：部署后端 (FastAPI)

#### 4.1 创建Python环境
```bash
cd /www/wwwroot/dreamfly/pybackend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 4.2 配置环境变量
创建 `/www/wwwroot/dreamfly/pybackend/.env` 文件：
```env
# 应用配置
APP_NAME=DreamFly API
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./dreamfly.db

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=20971520

# 意识体数据目录
MINDS_DIR=./database/minds

# CORS配置
CORS_ORIGINS=["https://your-domain.com"]

# AI模型配置
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3

# JWT认证配置
SECRET_KEY=your_jwt_secret_key_here_please_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

#### 4.3 初始化数据库
```bash
cd /www/wwwroot/dreamfly/pybackend
source venv/bin/activate
python init_db.py
```

#### 4.4 使用PM2管理后端进程
在宝塔面板 → PM2管理器 → 添加项目：

**项目配置**:
- **项目名称**: dreamfly-api
- **启动文件**: `/www/wwwroot/dreamfly/pybackend/venv/bin/uvicorn`
- **运行目录**: `/www/wwwroot/dreamfly/pybackend`
- **启动参数**: `main:app --host 0.0.0.0 --port 8000 --workers 4`

或者使用命令行：
```bash
cd /www/wwwroot/dreamfly/pybackend
pm2 start "venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4" --name dreamfly-api
pm2 save
pm2 startup
```

### 第五步：部署前端 (Vue.js)

#### 5.1 安装前端依赖
```bash
cd /www/wwwroot/dreamfly

# 安装依赖
npm install
```

#### 5.2 配置生产环境
编辑 `.env` 文件，设置生产环境：
```env
VUE_APP_ENVIRONMENT=production
VUE_APP_DEBUG=false
VUE_APP_DEV_API_BASE_URL=http://localhost:8000
VUE_APP_DEV_FRONTEND_URL=http://localhost:5173
VUE_APP_PROD_API_BASE_URL=https://api.your-domain.com
VUE_APP_PROD_FRONTEND_URL=https://your-domain.com
```

#### 5.3 构建前端
```bash
cd /www/wwwroot/dreamfly

# 构建生产版本
npm run build:h5:prod
```

构建完成后，静态文件位于 `dist/build/h5/` 目录。

### 第六步：配置Nginx

#### 6.1 创建网站
在宝塔面板 → 网站 → 添加站点：
- **域名**: your-domain.com
- **根目录**: `/www/wwwroot/dreamfly/dist/build/h5`

#### 6.2 配置Nginx规则
在网站设置 → 配置文件中添加以下配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /www/wwwroot/dreamfly/dist/build/h5;
    index index.html;

    # 启用gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # SPA路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### 6.3 配置SSL证书 (推荐)
在宝塔面板 → 网站 → SSL → 申请Let's Encrypt免费证书

### 第七步：配置防火墙

在宝塔面板 → 安全 → 防火墙 → 添加规则：
- **端口**: 8000 (后端API端口)
- **协议**: TCP
- **策略**: 放行
- **备注**: DreamFly API

## 🔧 部署脚本

创建自动化部署脚本 `/www/wwwroot/dreamfly/deploy-baota.sh`：

```bash
#!/bin/bash
# DreamFly 宝塔部署脚本

set -e

PROJECT_DIR="/www/wwwroot/dreamfly"
BACKEND_DIR="$PROJECT_DIR/pybackend"

echo "🚀 开始部署 DreamFly..."

# 1. 更新代码 (如果使用Git)
cd $PROJECT_DIR
if [ -d ".git" ]; then
    echo "📥 更新代码..."
    git pull origin main
fi

# 2. 更新后端依赖
echo "🔧 更新后端依赖..."
cd $BACKEND_DIR
source venv/bin/activate
pip install -r requirements.txt

# 3. 数据库迁移 (如果需要)
echo "🗄️ 检查数据库..."
python init_db.py

# 4. 重启后端服务
echo "🔄 重启后端服务..."
pm2 restart dreamfly-api

# 5. 构建前端
echo "🏗️ 构建前端..."
cd $PROJECT_DIR
npm install
npm run build:h5:prod

# 6. 重载Nginx
echo "🌐 重载Nginx..."
nginx -s reload

echo "✅ 部署完成！"
echo "🌐 访问地址: https://your-domain.com"
echo "📚 API文档: https://your-domain.com/api/docs"
```

给脚本执行权限：
```bash
chmod +x /www/wwwroot/dreamfly/deploy-baota.sh
```

## 📊 监控和维护

### 日志查看
```bash
# 查看后端日志
pm2 logs dreamfly-api

# 查看Nginx日志
tail -f /www/wwwroot/dreamfly/logs/access.log
tail -f /www/wwwroot/dreamfly/logs/error.log
```

### 服务管理
```bash
# 重启后端
pm2 restart dreamfly-api

# 查看服务状态
pm2 status

# 重载Nginx
nginx -s reload
```

### 定时任务
在宝塔面板 → 计划任务 → 添加任务：
- **任务类型**: Shell脚本
- **任务名称**: DreamFly数据库备份
- **执行周期**: 每天凌晨2点
- **脚本内容**:
```bash
#!/bin/bash
BACKUP_DIR="/www/backup/dreamfly"
mkdir -p $BACKUP_DIR
cp /www/wwwroot/dreamfly/pybackend/dreamfly.db $BACKUP_DIR/dreamfly_$(date +%Y%m%d_%H%M%S).db
# 保留最近7天的备份
find $BACKUP_DIR -name "dreamfly_*.db" -mtime +7 -delete
```

## 🔍 故障排除

### 常见问题

1. **后端启动失败**
   ```bash
   # 检查Python环境
   cd /www/wwwroot/dreamfly/pybackend
   source venv/bin/activate
   python -c "import fastapi; print('FastAPI OK')"
   
   # 检查端口占用
   netstat -tulpn | grep :8000
   ```

2. **前端访问404**
   ```bash
   # 检查构建文件
   ls -la /www/wwwroot/dreamfly/dist/build/h5/
   
   # 检查Nginx配置
   nginx -t
   ```

3. **API跨域问题**
   - 检查 `.env` 文件中的 `CORS_ORIGINS` 配置
   - 确保域名配置正确

4. **数据库权限问题**
   ```bash
   # 设置数据库文件权限
   chown -R www:www /www/wwwroot/dreamfly/pybackend/
   chmod 755 /www/wwwroot/dreamfly/pybackend/dreamfly.db
   ```

## 🔒 安全建议

1. **修改默认密钥**: 确保 `.env` 文件中的 `SECRET_KEY` 使用强密码
2. **API密钥保护**: 妥善保管 `SILICONFLOW_API_KEY`
3. **文件权限**: 设置合适的文件权限，避免敏感文件泄露
4. **定期备份**: 设置自动备份数据库和重要文件
5. **SSL证书**: 启用HTTPS加密传输
6. **防火墙**: 只开放必要的端口

## 📞 技术支持

部署过程中如遇问题，请检查：
1. 宝塔面板版本是否最新
2. Python和Node.js版本是否符合要求
3. 网络连接是否正常
4. 域名DNS解析是否正确
5. 防火墙和安全组配置是否正确
