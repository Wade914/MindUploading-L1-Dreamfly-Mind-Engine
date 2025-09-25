# 云己意识上传平台 API 文档 v1.0

## 基础信息
- 基础URL: `https://api.dreamfly.ai/v1`
- 所有请求都需要在header中携带token: `Authorization: Bearer <token>`
- 响应格式统一为JSON
- 时间格式统一为ISO 8601: `YYYY-MM-DDTHH:mm:ssZ`

## 1. 用户认证模块

### 1.1 用户注册
```http
POST /auth/register

请求体：
{
  "username": string,     // 用户名
  "password": string,     // 密码
  "email": string,        // 邮箱
  "birth": string        // 出生日期，格式：YYYY-MM-DD
}

响应：
{
  "code": 200,
  "data": {
    "user_id": string,
    "username": string,
    "token": string,      // JWT token
    "created_at": string  // 注册时间
  }
}
```

### 1.2 用户登录
```http
POST /auth/login

请求体：
{
  "username": string,     // 用户名
  "password": string      // 密码
}

响应：
{
  "code": 200,
  "data": {
    "user_id": string,
    "username": string,
    "token": string,      // JWT token
    "last_login": string  // 上次登录时间
  }
}
```

## 2. 意识体创建模块

### 2.1 上传基础信息
```http
POST /mindcopy/basic

请求体：
{
  "name": string,           // 姓名
  "birth": string,          // 出生日期
  "occupation": string,     // 职业
  "self_cognition": string, // 自我认知描述
  "memories": [             // 记忆片段数组
    {
      "time": string,       // 记忆时间
      "content": string     // 记忆内容
    }
  ]
}

响应：
{
  "code": 200,
  "data": {
    "mind_id": string,     // 意识体ID
    "created_at": string
  }
}
```

### 2.2 上传声音数据
```http
POST /mindcopy/voice

请求体：
{
  "mind_id": string,       // 意识体ID
  "voice_file": File,      // 声音文件
  "duration": number       // 时长（秒）
}

响应：
{
  "code": 200,
  "data": {
    "voice_id": string,
    "voice_url": string,
    "uploaded_at": string
  }
}
```

### 2.3 上传形象数据
```http
POST /mindcopy/image

请求体：
{
  "mind_id": string,      // 意识体ID
  "image_file": File,     // 图片文件
  "height": number,       // 身高(cm)
  "weight": number        // 体重(kg)
}

响应：
{
  "code": 200,
  "data": {
    "image_id": string,
    "image_url": string,
    "uploaded_at": string
  }
}
```

### 2.4 生成意识体文件
```http
POST /mindcopy/generate

请求体：
{
  "mind_id": string       // 意识体ID
}

响应：
{
  "code": 200,
  "data": {
    "mind_file": string,  // .mind文件下载URL
    "generated_at": string
  }
}
```

## 3. 梦蝶心智引擎模块

### 3.1 加载意识体
```http
POST /interaction/load

请求体：
{
  "mind_file": string     // .mind文件内容
}

响应：
{
  "code": 200,
  "data": {
    "session_id": string,
    "consciousness_status": {
      "name": string,
      "anti_program_ratio": number,
      "connection_degree": number,
      "life_days": number
    }
  }
}
```

### 3.2 与意识体对话
```http
POST /interaction/chat

请求体：
{
  "session_id": string,   // 会话ID
  "message": string       // 用户输入的消息
}

响应：
{
  "code": 200,
  "data": {
    "response": string,   // 意识体的回复
    "emotion": string,    // 情感状态
    "tokens": number      // 消耗的token数量
  }
}
```

### 3.3 获取会话历史
```http
GET /interaction/history?session_id={session_id}

响应：
{
  "code": 200,
  "data": {
    "messages": [
      {
        "role": string,     // "user" 或 "assistant"
        "content": string,  // 消息内容
        "timestamp": string // 发送时间
      }
    ]
  }
}
```

### 3.4 结束会话
```http
POST /interaction/end

请求体：
{
  "session_id": string    // 会话ID
}

响应：
{
  "code": 200,
  "data": {
    "session_duration": number,  // 会话时长（秒）
    "total_tokens": number,      // 总消耗token数
    "ended_at": string
  }
}
```

## 错误码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项

1. 文件上传大小限制：
   - 声音文件：最大50MB
   - 图片文件：最大10MB
   - .mind文件：最大5MB

2. 接口限流说明：
   - 注册/登录接口：每IP每分钟最多10次
   - 对话接口：每用户每分钟最多60次
   - 文件上传接口：每用户每小时最多100次

3. Token有效期：
   - JWT token有效期为7天
   - 超过5天后可以通过旧token获取新token
   - token失效后需要重新登录 