# DreamFly 记忆中心接口文档

## 基础信息

- 基础路径: `/api/v1`
- 响应格式: JSON
- 认证方式: Bearer Token

## 1. 统计信息接口

### 1.1 获取记忆中心统计数据
```
GET /memory/statistics

响应：
{
  "code": 200,
  "data": {
    "totalMemories": number,    // 记忆片段总数
    "totalDiaries": number      // 日记总数
  }
}
```

## 2. 生命记忆模块

### 2.1 获取记忆列表
```
GET /memories
参数：
- filter: string (可选, 'all' | 'childhood' | 'youth' | 'adulthood')
- page: number
- pageSize: number

响应：
{
  "code": 200,
  "data": {
    "total": number,
    "list": [
      {
        "id": string,
        "title": string,
        "time": string,
        "content": string,
        "tags": string[],
        "createdAt": string,
        "updatedAt": string
      }
    ]
  }
}
```

### 2.2 创建新记忆
```
POST /memories
请求体：
{
  "title": string,
  "time": string,
  "content": string,
  "tags": string[]
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "title": string,
    "time": string,
    "content": string,
    "tags": string[],
    "createdAt": string
  }
}
```

### 2.3 更新记忆
```
PUT /memories/:id
请求体：
{
  "title": string,
  "time": string,
  "content": string,
  "tags": string[]
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "updatedAt": string
  }
}
```

### 2.4 删除记忆
```
DELETE /memories/:id

响应：
{
  "code": 200,
  "message": "删除成功"
}
```

## 3. 日常心声模块

### 3.1 获取日记列表
```
GET /diaries
参数：
- mood: string (可选, 'all' | 'happy' | 'sad' | 'angry' | 'peaceful')
- page: number
- pageSize: number

响应：
{
  "code": 200,
  "data": {
    "total": number,
    "list": [
      {
        "id": string,
        "date": string,
        "mood": string,
        "content": string,
        "source": string,
        "createdAt": string
      }
    ]
  }
}
```

### 3.2 创建新日记
```
POST /diaries
请求体：
{
  "date": string,
  "mood": string,
  "content": string,
  "source": string
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

### 3.3 导入社交媒体内容
```
POST /diaries/import
请求体：
{
  "platform": string,  // 'weibo' | 'jike' | 'xiaohongshu'
  "content": string,
  "date": string,
  "mood": string
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

## 4. 个人传记模块

### 4.1 获取传记章节列表
```
GET /biography/chapters

响应：
{
  "code": 200,
  "data": {
    "chapters": [
      {
        "id": string,
        "title": string,
        "content": string,
        "progress": number,
        "memories": string[],  // 关联的记忆ID数组
        "createdAt": string,
        "updatedAt": string
      }
    ]
  }
}
```

### 4.2 创建新章节
```
POST /biography/chapters
请求体：
{
  "title": string,
  "content": string,
  "memories": string[]  // 关联的记忆ID数组
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

### 4.3 更新章节
```
PUT /biography/chapters/:id
请求体：
{
  "title": string,
  "content": string,
  "memories": string[]
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "updatedAt": string
  }
}
```

### 4.4 AI内容生成
```
POST /biography/ai/generate
请求体：
{
  "chapterId": string,
  "prompt": string
}

响应：
{
  "code": 200,
  "data": {
    "content": string
  }
}
```

### 4.5 AI内容润色
```
POST /biography/ai/polish
请求体：
{
  "content": string,
  "style": string  // 'narrative' | 'literary' | 'concise' | 'detailed'
}

响应：
{
  "code": 200,
  "data": {
    "content": string
  }
}
```

## 5. 错误码说明

```
200: 成功
400: 请求参数错误
401: 未授权
403: 禁止访问
404: 资源不存在
500: 服务器内部错误
```

## 6. 数据模型

### 6.1 记忆 (Memory)
```typescript
interface Memory {
  id: string;
  title: string;
  time: string;
  content: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}
```

### 6.2 日记 (Diary)
```typescript
interface Diary {
  id: string;
  date: string;
  mood: string;
  content: string;
  source?: string;
  createdAt: string;
  updatedAt: string;
}
```

### 6.3 传记章节 (Chapter)
```typescript
interface Chapter {
  id: string;
  title: string;
  content: string;
  progress: number;
  memories: string[];
  createdAt: string;
  updatedAt: string;
}
```

## 7. 注意事项

1. 所有时间字段使用 ISO 8601 格式
2. 分页接口默认每页 20 条数据
3. AI 相关接口可能需要较长处理时间，建议添加超时处理
4. 文本内容支持 Markdown 格式
5. 所有接口都需要进行用户认证
6. 建议实现数据缓存机制，提高访问速度
7. 图片等媒体内容建议使用单独的文件上传接口
8. 需要考虑数据备份和恢复机制

## 8. 知识库模块

### 8.1 获取知识点列表
```
GET /knowledge/nodes
参数：
- type: string (可选, 'all' | 'book' | 'note')
- keyword: string (可选，搜索关键词)
- page: number
- pageSize: number

响应：
{
  "code": 200,
  "data": {
    "total": number,
    "list": [
      {
        "id": string,
        "title": string,
        "content": string,
        "type": string,
        "tags": string[],
        "connections": Array<{
          "nodeId": string,
          "relationship": string
        }>,
        "createdAt": string,
        "updatedAt": string
      }
    ]
  }
}
```

### 8.2 创建知识点
```
POST /knowledge/nodes
请求体：
{
  "title": string,
  "content": string,
  "type": string,
  "tags": string[],
  "connections": Array<{
    "nodeId": string,
    "relationship": string
  }>
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

### 8.3 更新知识点
```
PUT /knowledge/nodes/:id
请求体：
{
  "title": string,
  "content": string,
  "tags": string[],
  "connections": Array<{
    "nodeId": string,
    "relationship": string
  }>
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "updatedAt": string
  }
}
```

### 8.4 获取知识图谱
```
GET /knowledge/graph
参数：
- layout: string (可选, 'network' | 'tree')
- rootId: string (可选，树形布局的根节点ID)

响应：
{
  "code": 200,
  "data": {
    "nodes": Array<{
      "id": string,
      "title": string,
      "type": string
    }>,
    "edges": Array<{
      "source": string,
      "target": string,
      "relationship": string
    }>
  }
}
```

## 9. 社交关系模块

### 9.1 获取关系列表
```
GET /social/relationships
参数：
- category: string (可选, 'all' | 'family' | 'friend' | 'colleague')
- page: number
- pageSize: number

响应：
{
  "code": 200,
  "data": {
    "total": number,
    "list": [
      {
        "id": string,
        "name": string,
        "category": string,
        "avatar": string,
        "description": string,
        "tags": string[],
        "interactions": Array<{
          "type": string,
          "date": string,
          "note": string
        }>,
        "createdAt": string,
        "updatedAt": string
      }
    ]
  }
}
```

### 9.2 创建关系
```
POST /social/relationships
请求体：
{
  "name": string,
  "category": string,
  "avatar": string,
  "description": string,
  "tags": string[]
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

### 9.3 记录互动
```
POST /social/relationships/:id/interactions
请求体：
{
  "type": string,
  "date": string,
  "note": string
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

### 9.4 获取社交网络图
```
GET /social/network
参数：
- timeRange: string (可选, 'week' | 'month' | 'year' | 'all')

响应：
{
  "code": 200,
  "data": {
    "nodes": Array<{
      "id": string,
      "name": string,
      "category": string,
      "avatar": string
    }>,
    "edges": Array<{
      "source": string,
      "target": string,
      "strength": number,
      "interactions": number
    }>
  }
}
```

## 10. 图灵对话模块

### 10.1 获取对话历史
```
GET /turing/conversations
参数：
- page: number
- pageSize: number

响应：
{
  "code": 200,
  "data": {
    "total": number,
    "list": [
      {
        "id": string,
        "topic": string,
        "messages": Array<{
          "role": string,
          "content": string,
          "timestamp": string
        }>,
        "createdAt": string,
        "updatedAt": string
      }
    ]
  }
}
```

### 10.2 发送消息
```
POST /turing/conversations/:id/messages
请求体：
{
  "content": string,
  "context": {
    "memories": string[],  // 相关记忆ID
    "knowledge": string[]  // 相关知识点ID
  }
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "content": string,
    "references": {
      "memories": Array<{
        "id": string,
        "title": string
      }>,
      "knowledge": Array<{
        "id": string,
        "title": string
      }>
    },
    "createdAt": string
  }
}
```

### 10.3 创建新对话
```
POST /turing/conversations
请求体：
{
  "topic": string,
  "initialMessage": string
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "createdAt": string
  }
}
```

## 11. 个性分析模块

### 11.1 获取性格特征
```
GET /personality/traits

响应：
{
  "code": 200,
  "data": {
    "traits": {
      "openness": number,
      "conscientiousness": number,
      "extraversion": number,
      "agreeableness": number,
      "neuroticism": number
    },
    "lastUpdated": string
  }
}
```

### 11.2 获取行为分析
```
GET /personality/behaviors
参数：
- timeRange: string (可选, 'week' | 'month' | 'year')

响应：
{
  "code": 200,
  "data": {
    "activities": Array<{
      "category": string,
      "frequency": number,
      "trend": string
    }>,
    "emotions": Array<{
      "type": string,
      "percentage": number
    }>,
    "interests": Array<{
      "category": string,
      "score": number
    }>,
    "period": {
      "start": string,
      "end": string
    }
  }
}
```

### 11.3 获取成长报告
```
GET /personality/growth
参数：
- year: number
- month: number (可选)

响应：
{
  "code": 200,
  "data": {
    "summary": string,
    "highlights": Array<{
      "category": string,
      "title": string,
      "description": string,
      "date": string
    }>,
    "improvements": Array<{
      "aspect": string,
      "before": number,
      "after": number,
      "suggestion": string
    }>,
    "period": {
      "start": string,
      "end": string
    }
  }
}
```

## 12. 补充数据模型

### 12.1 知识点 (KnowledgeNode)
```typescript
interface KnowledgeNode {
  id: string;
  title: string;
  content: string;
  type: 'book' | 'note';
  tags: string[];
  connections: Array<{
    nodeId: string;
    relationship: string;
  }>;
  createdAt: string;
  updatedAt: string;
}
```

### 12.2 社交关系 (Relationship)
```typescript
interface Relationship {
  id: string;
  name: string;
  category: string;
  avatar: string;
  description: string;
  tags: string[];
  interactions: Array<{
    type: string;
    date: string;
    note: string;
  }>;
  createdAt: string;
  updatedAt: string;
}
```

### 12.3 对话 (Conversation)
```typescript
interface Conversation {
  id: string;
  topic: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  createdAt: string;
  updatedAt: string;
}
```

### 12.4 个性特征 (PersonalityTrait)
```typescript
interface PersonalityTrait {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
  lastUpdated: string;
}
```

## 13. 意识上传模块

### 13.1 上传图片数据
```
POST /consciousness/upload/image
请求体：
{
  "image": File,  // 图片文件
  "metadata": {
    "description": string,
    "timestamp": string,
    "location": string
  }
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "url": string,
    "uploadedAt": string
  }
}
```

### 13.2 上传语音数据
```
POST /consciousness/upload/voice
请求体：
{
  "audio": File,  // 音频文件
  "metadata": {
    "duration": number,
    "timestamp": string,
    "language": string
  }
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "url": string,
    "uploadedAt": string
  }
}
```

### 13.3 上传思维数据
```
POST /consciousness/upload/mind
请求体：
{
  "thoughts": Array<{
    "content": string,
    "timestamp": string,
    "emotion": string,
    "tags": string[]
  }>
}

响应：
{
  "code": 200,
  "data": {
    "id": string,
    "uploadedAt": string
  }
}
```

### 13.4 生成意识体
```
POST /consciousness/generate
请求体：
{
  "imageId": string,
  "voiceId": string,
  "mindId": string,
  "parameters": {
    "personality": {
      "openness": number,
      "conscientiousness": number,
      "extraversion": number,
      "agreeableness": number,
      "neuroticism": number
    },
    "preferences": {
      "language": string,
      "communicationStyle": string,
      "interests": string[]
    }
  }
}

响应：
{
  "code": 200,
  "data": {
    "taskId": string,
    "status": string,
    "estimatedTime": number
  }
}
```

### 13.5 获取生成进度
```
GET /consciousness/generate/:taskId

响应：
{
  "code": 200,
  "data": {
    "status": string,
    "progress": number,
    "currentStep": string,
    "estimatedTime": number
  }
}
```

### 13.6 下载意识体文件
```
GET /consciousness/download/:id

响应：
{
  "code": 200,
  "data": {
    "url": string,
    "expiresAt": string,
    "fileSize": number
  }
}
```

### 13.7 数据模型

#### 13.7.1 图片数据 (ImageData)
```typescript
interface ImageData {
  id: string;
  url: string;
  metadata: {
    description: string;
    timestamp: string;
    location: string;
  };
  uploadedAt: string;
}
```

#### 13.7.2 语音数据 (VoiceData)
```typescript
interface VoiceData {
  id: string;
  url: string;
  metadata: {
    duration: number;
    timestamp: string;
    language: string;
  };
  uploadedAt: string;
}
```

#### 13.7.3 思维数据 (MindData)
```typescript
interface MindData {
  id: string;
  thoughts: Array<{
    content: string;
    timestamp: string;
    emotion: string;
    tags: string[];
  }>;
  uploadedAt: string;
}
```

#### 13.7.4 意识体文件 (ConsciousnessFile)
```typescript
interface ConsciousnessFile {
  id: string;
  version: string;
  components: {
    image: ImageData;
    voice: VoiceData;
    mind: MindData;
  };
  parameters: {
    personality: PersonalityTrait;
    preferences: {
      language: string;
      communicationStyle: string;
      interests: string[];
    };
  };
  generatedAt: string;
  fileSize: number;
}
```

### 13.8 注意事项

1. 所有文件上传接口需要支持断点续传
2. 文件大小限制：
   - 图片：最大 10MB
   - 音频：最大 50MB
   - 意识体文件：最大 1GB
3. 支持的文件格式：
   - 图片：JPG, PNG, WebP
   - 音频：MP3, WAV, OGG
4. 生成过程可能需要较长时间，建议实现进度查询和通知机制
5. 意识体文件需要加密存储，确保数据安全
6. 建议实现文件版本控制，支持回滚和更新
7. 需要实现数据备份和恢复机制
8. 所有接口都需要进行用户认证和权限验证 