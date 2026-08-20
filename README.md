# 反诈大师 - AI 智能反诈助手

## 项目简介

**反诈大师**是一个基于 Spring Boot + Python LangChain + 阿里云百炼大模型构建的智能反诈骗助手系统。系统支持多模态交互（文本、语音、图片、视频），能够智能识别诈骗风险，为不同角色群体（财会人员、自由职业者、老人、青年、少儿）提供个性化的反诈防护服务。

## 系统架构

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  前端 Vue 3   │    │  Java 后端    │    │ Python 微服务 │
│  (Web/小程序)  │───▶│ Spring Boot  │───▶│ LangChain    │
│              │    │  REST API    │    │ DashScope    │
└──────────────┘    └──────────────┘    └──────────────┘
                          │                    │
                          ▼                    ▼
                    ┌──────────────┐    ┌──────────────┐
                    │   MySQL 8.0   │    │  ChromaDB    │
                    │  (用户/业务)   │    │  (向量存储)   │
                    └──────────────┘    └──────────────┘
```

### 核心架构说明
- **Java 后端**：Spring Boot 3.3.3，负责业务逻辑、用户认证、API 路由
- **Python 微服务**：FastAPI + LangChain，负责所有 AI 功能（对话、RAG、视觉分析等）
- **AI 模型**：阿里云百炼（DashScope），提供大模型能力
- **数据存储**：MySQL 8.0.24（用户信息 + 业务数据）+ ChromaDB（向量存储）

## 核心功能

### 1. 多模态交互
- **文本对话**：支持自然语言对话，智能识别诈骗风险
- **图片识别**：上传图片，通过视觉大模型（qwen-vl-max）识别图片中的诈骗内容
- **视频支持**：支持视频文件上传与分析

### 2. 角色化服务
系统支持五大角色群体，提供个性化反诈服务：
- 财会人员 - 铁面审计官
- 自由职业者 - 搞钱搭子
- 老人 - 银发守护者
- 青年 - 反诈战友
- 少儿 - 安全守护精灵

### 3. 智能风险检测
- 实时风险等级评估（低/中/高/极高）
- 诈骗类型识别（刷单、杀猪盘、冒充公检法等）
- 自动生成安全报告

### 4. 知识库问答（RAG）
- 基于 LangChain + ChromaDB 的向量检索增强
- 支持多场景问答（闲聊、科普、风险检测）
- 分角色知识库内容

## 技术栈

### 后端技术栈
| 技术 | 版本 | 说明 |
|------|------|------|
| Spring Boot | 3.3.3 | Java 基础框架 |
| Python | 3.10 | AI 微服务 |
| FastAPI | 0.100+ | Python Web 框架 |
| LangChain | 0.3+ | AI 应用开发框架 |
| LangChain-DashScope | 0.2+ | 阿里云百炼集成 |
| MySQL | 8.0.24 | 用户/业务数据存储 |
| ChromaDB | 0.4+ | 向量存储 |

### 前端技术栈
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue.js | 3.x | 前端框架 |
| Vite | 4.x | 构建工具 |
| UniApp | - | 微信小程序 |

### AI 模型
| 模型 | 用途 |
|------|------|
| qwen-plus | 对话生成 |
| qwen-vl-max | 图片识别（OCR + 场景理解） |
| text-embedding-v2 | 文本向量化 |

## 快速开始

### 环境要求
- JDK 17+
- Python 3.10+
- Node.js 18+
- Maven 3.6+
- MySQL 8.0.24

### 1. 初始化数据库
```sql
-- 执行数据库初始化脚本
source database/init.sql
```

### 2. 配置环境变量

**Python 微服务**（`python_services/.env`）：
```env
DASHSCOPE_API_KEY=your-api-key-here
```

### 3. 启动 Python 微服务
```bash
cd python_services
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8501
```

### 4. 启动 Java 后端
```bash
cd antiFraud-ai-agent
mvn spring-boot:run
```

后端服务启动在 `http://localhost:8123/api`

## API 接口

### AI 对话接口
```
POST /api/ai/chat          # 基础对话
POST /api/ai/chat/stream   # 流式对话（SSE）
POST /api/ai/chat/tools    # 带工具对话
POST /api/ai/chat/report   # 报告生成对话
```

### 视觉分析接口
```
POST /api/ai/vision/analyze  # 图片分析
```

### RAG 接口
```
POST /api/ai/rag/chat    # RAG 对话
POST /api/ai/rag/search  # 知识检索
```

### 用户认证接口
```
POST /api/auth/login     # 登录
POST /api/auth/register  # 注册
```

### 健康检查
```
GET /api/health
```

## 核心特性

### 1. 对话三模式
- **闲聊模式**：最高优先级，温暖自然的口语化交流
- **咨询模式**：知识性问答，精准匹配知识库
- **反诈预警模式**：个人遭遇分析，四段式专业回复

### 2. 视觉大模型图片识别
- 使用 qwen-vl-max 模型进行 OCR 文字提取
- 自动识别图片中的诈骗关键词
- 支持多种图片格式

### 3. 风险评估
- 四级风险等级（低/中/高/极高）
- 多维度加权评分
- 安全建议生成

## 知识库

系统内置五大角色专属知识库：
- **老年篇**：保健品诈骗、以房养老诈骗等
- **青年篇**：刷单诈骗、杀猪盘等
- **少儿篇**：游戏充值诈骗、免费皮肤诈骗等
- **财会篇**：冒充老板诈骗、虚假发票等
- **自由职业者篇**：兼职诈骗、虚假合作等