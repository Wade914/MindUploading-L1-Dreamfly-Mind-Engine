# DreamFly API 测试指南

## 📋 测试脚本说明

本项目提供了多个测试脚本来验证 API 功能：

### 1. 🔧 语法检查脚本
```bash
python check_syntax.py
```
- **作用**: 检查所有 Python 文件的语法是否正确
- **适用场景**: 开发阶段，确保代码没有语法错误

### 2. 📦 导入测试脚本
```bash
python test_imports.py
```
- **作用**: 测试所有模块的导入是否正常
- **适用场景**: 安装依赖后，验证模块导入

### 3. 🌐 完整 API 测试脚本（异步版）
```bash
python test_api.py
```
- **依赖**: 需要安装 `httpx` 库
- **功能**: 全面测试所有 API 端点
- **特点**: 异步请求，支持自定义服务器地址

### 4. 🚀 简单 API 测试脚本（推荐）
```bash
python test_api_simple.py
```
- **依赖**: 只需要 `requests` 库（通常已安装）
- **功能**: 测试主要 API 端点
- **特点**: 同步请求，简单易用

## 🎯 使用步骤

### 第一步：启动服务器
```bash
# 方式1：使用启动脚本（推荐）
python start.py

# 方式2：直接启动
python main.py
```

### 第二步：运行测试
```bash
# 推荐使用简单版本
python test_api_simple.py

# 或者使用完整版本
python test_api.py
```

### 第三步：查看结果
测试脚本会显示：
- ✅ 通过的测试
- ❌ 失败的测试
- 📊 统计信息

## 🧪 测试内容

### 基础连接测试
- [x] 服务器健康检查 (`/health`)
- [x] 根路径访问 (`/`)
- [x] API 文档访问 (`/docs`)

### 认证功能测试
- [x] 用户注册 (`POST /api/register`)
- [x] 用户登录 (`POST /api/login`)

### 意识体功能测试
- [x] 获取意识体列表 (`GET /api/mind-list`)
- [x] 创建意识体 (`POST /api/mind`)

### AI 服务测试
- [x] 获取模型列表 (`GET /api/ai/models`)

## 🔧 自定义测试

### 测试不同服务器地址
```bash
python test_api_simple.py http://your-server:8000
```

### 添加新的测试用例
编辑 `test_api_simple.py`，在 `SimpleAPITester` 类中添加新方法：

```python
def test_your_endpoint(self):
    """测试你的端点"""
    try:
        response = self.session.get(f"{self.base_url}/your/endpoint")
        if response.status_code == 200:
            self.log_test("你的测试", True, "测试通过")
            return True
        else:
            self.log_test("你的测试", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        self.log_test("你的测试", False, f"请求失败: {str(e)}")
        return False
```

然后在 `run_all_tests()` 方法中调用：
```python
self.test_your_endpoint()
```

## 🐛 常见问题

### 1. 连接失败
```
❌ 服务器连接: 连接失败: Connection refused
```
**解决方案**:
- 确保服务器正在运行
- 检查端口是否正确（默认8000）
- 检查防火墙设置

### 2. 模块导入失败
```
❌ 导入错误: No module named 'fastapi'
```
**解决方案**:
```bash
pip install -r requirements.txt
```

### 3. 数据库错误
```
❌ 创建意识体: API错误: 数据库连接失败
```
**解决方案**:
```bash
python init_db.py  # 初始化数据库
```

### 4. 配置错误
```
❌ AI模型列表: API错误: SiliconFlow API Key 未配置
```
**解决方案**:
- 复制 `.env.example` 为 `.env`
- 配置必要的 API Key

## 📈 测试结果示例

```
🚀 DreamFly API 简单测试开始...
==================================================
✅ 服务器连接: 服务器正常运行
✅ 根路径: 响应: DreamFly API is running!
✅ API文档: 文档页面可访问
✅ 意识体列表: 找到 15 个文件
✅ AI模型列表: 聊天模型: 1, 语音模型: 1
✅ 用户注册: 用户ID: 12345678-1234-1234-1234-123456789abc
✅ 创建意识体: 意识体ID: 87654321-4321-4321-4321-cba987654321

==================================================
📊 测试结果统计:
总测试数: 7
✅ 通过: 7
❌ 失败: 0
成功率: 100.0%

🎉 所有测试通过！API 运行正常！
```

## 🎉 成功标准

当看到以下结果时，说明 API 运行正常：
- 服务器连接成功
- 所有基础端点响应正常
- 数据库操作正常
- 成功率 > 80%

现在你可以开始测试你的 DreamFly API 了！
