# Square页面迁移文档 📚

## 📖 文档索引

本目录包含了Square广场功能从Vue组件迁移到HTML+web-view架构的完整文档。

### 1️⃣ [square页面完整迁移完成说明.md](./square页面完整迁移完成说明.md)
**内容**：迁移工作的完整说明
- 迁移背景和原因
- 技术架构变更
- 文件结构对比
- 使用说明
- 下一步计划

**适合阅读对象**：需要了解整体迁移方案的开发者

---

### 2️⃣ [square页面跳转逻辑说明.md](./square页面跳转逻辑说明.md)
**内容**：页面间跳转逻辑的详细说明
- 导航函数实现
- 所有修改的跳转链接
- 跳转流程图
- 测试清单
- 常见问题解答

**适合阅读对象**：需要维护或添加新页面的开发者

---

### 3️⃣ [square页面迁移完成检查清单.md](./square页面迁移完成检查清单.md)
**内容**：迁移工作的完整检查清单
- 7个任务的详细完成情况
- 每个文件的修改记录
- 完成度统计
- 测试清单

**适合阅读对象**：需要验证迁移完成度的开发者或项目经理

---

### 4️⃣ [广场页面web-view改造完成说明.md](./广场页面web-view改造完成说明.md)
**内容**：早期web-view改造的说明文档
- web-view架构介绍
- 改造步骤
- 文件结构

**适合阅读对象**：需要了解web-view架构的开发者

---

### 5️⃣ [广场页面样式修复指南.md](./广场页面样式修复指南.md)
**内容**：HTML和Vue版本样式差异的修复指南
- 样式不一致问题分析
- 修复方案
- 对比说明

**适合阅读对象**：需要处理样式问题的前端开发者

---

## 🎯 快速开始

### 查看迁移概览
```bash
# 阅读完整迁移说明
cat docs/square-migration/square页面完整迁移完成说明.md
```

### 了解跳转逻辑
```bash
# 阅读跳转逻辑说明
cat docs/square-migration/square页面跳转逻辑说明.md
```

### 检查完成情况
```bash
# 阅读检查清单
cat docs/square-migration/square页面迁移完成检查清单.md
```

---

## 📊 迁移总结

### **完成度**：85.7% (6/7)

### **已完成**：
- ✅ 迁移5个HTML页面到static目录
- ✅ 迁移7个CSS/JS文件
- ✅ 创建5个Vue web-view容器
- ✅ 注册5个新路由
- ✅ 为所有页面添加API配置
- ✅ 配置完整的跳转逻辑

### **待完成**：
- ⏳ 测试所有页面加载和跳转功能

---

## 🔗 相关文件

### **HTML页面**：
- `static/square/square.html` - 广场主页
- `static/square/homepage.html` - 个人主页
- `static/square/profile.html` - 用户资料
- `static/square/mindos.html` - MindOS
- `static/square/wittgenstein.html` - 维特根斯坦

### **Vue容器**：
- `src/pages/square/index.vue` - 广场主页容器
- `src/pages/square/homepage/index.vue` - 个人主页容器
- `src/pages/square/profile/index.vue` - 用户资料容器
- `src/pages/square/mindos/index.vue` - MindOS容器
- `src/pages/square/wittgenstein/index.vue` - 维特根斯坦容器

### **核心配置**：
- `static/square/js/api-config.js` - API配置和导航函数
- `src/pages.json` - 路由配置（第106-145行）

---

## 📝 更新日志

### 2025-10-20
- ✅ 完成所有HTML页面迁移
- ✅ 完成所有Vue容器创建
- ✅ 完成路由注册
- ✅ 完成API配置
- ✅ 完成跳转逻辑配置
- ✅ 修复square.html的API配置引用问题
- ✅ 生成完整文档

---

## 🐾 维护说明

### **添加新页面**：
1. 在 `static/square/` 创建新的HTML文件
2. 在 `src/pages/square/` 创建对应的Vue容器
3. 在 `src/pages.json` 注册新路由
4. 在 `api-config.js` 的 `navigateTo()` 函数中添加路由映射
5. 在HTML中添加 `<script src="./js/api-config.js"></script>`

### **修改跳转逻辑**：
1. 编辑 `static/square/js/api-config.js`
2. 修改 `navigateTo()` 函数中的路由映射表
3. 在HTML中使用 `href="javascript:navigateTo('pageName')"`

### **开发后端API**：
1. 在 `pybackend/api/endpoints/` 创建新的API端点
2. 在 `api-config.js` 中添加对应的API调用函数
3. 设置 `MOCK_ENABLED = false` 启用真实API

---

有任何问题请参考上述文档或联系开发团队 🐾

