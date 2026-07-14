# 反诈大师 - AI 智能反诈助手

## 项目简介

**反诈大师**是一个基于 Spring Boot + Spring AI + 阿里云百炼大模型构建的智能反诈骗助手系统。系统支持多模态交互（文本、语音、图片、视频），能够智能识别诈骗风险，为不同角色群体（财会人员、自由职业者、老人、青年、少儿）提供个性化的反诈防护服务。

## 核心功能

### 1. 多模态交互
- **文本对话**：支持自然语言对话，智能识别诈骗风险
- **语音识别**：上传音频文件，自动转文字并分析
- **图片识别**：上传图片，通过视觉大模型（qwen-vl-max）识别图片中的诈骗内容
- **视频支持**：支持视频文件上传与分析

### 2. 角色化服务
系统支持五大角色群体，提供个性化反诈服务：
 角色           场景人设 
 财会人员        铁面审计官（资深注册会计师） 
 自由职业者      搞钱搭子（资深自由职业者） 
 老人           银发守护者（老邻居/忘年交） 
 青年           反诈战友（死党/知心大哥） 
 少儿           安全守护精灵（卡通小卫士） 

### 3. 智能风险检测
- 实时风险等级评估（低/中/高风险）
- 诈骗类型识别（刷单、杀猪盘、冒充公检法等）
- 自动生成安全报告

### 4. 知识库问答
- 基于阿里云百炼知识库的 RAG 检索增强
- 支持多场景问答（闲聊、科普、风险检测）
- 分角色知识库内容

## 技术架构

### 后端技术栈
| 技术 | 版本 | 说明 |
|------|------|------|
| Spring Boot | 3.3.3 | 基础框架 |
| Spring AI | 1.0.0 | AI 能力集成 |
| Spring AI Alibaba | 1.0.0.2 | 阿里云百炼集成 |
| DashScope SDK | 2.19.1 | 阿里云大模型 SDK |
| LangChain4j | 1.0.0-beta2 | AI 应用开发框架 |

### 前端技术栈
| 技术 | 版本 | 说明 |
|------|------|------|
| Vue.js | 3.x | 前端框架 |
| Vite | 4.x | 构建工具 |
| SSE | - | 服务端推送事件 |

### AI 模型
| 模型 | 用途 |
|------|------|
| qwen-max | 对话生成 |
| qwen-vl-max | 图片识别（OCR + 场景理解） |
| paraformer-v2 | 语音识别 |

## 项目结构

```
yu-ai-agent/
├── src/main/java/com/yuqi/yuaiagent/
│   ├── agent/                    # AI Agent 实现
│   │   ├── BaseAgent.java        # Agent 基类
│   │   ├── ReActAgent.java       # ReAct 模式 Agent
│   │   ├── ToolCallAgent.java    # 工具调用 Agent
│   │   └── YuManus.java          # Manus 多步骤 Agent
│   ├── app/                      # 应用层
│   │   ├── LoveApp.java          # 核心对话应用
│   │   └── MultimodalityApp.java # 多模态应用
│   ├── controller/               # 控制器层
│   │   ├── AiController.java     # AI 接口
│   │   └── HealthController.java # 健康检查
│   ├── rag/                      # RAG 检索增强
│   │   ├── LoveAppRagCloudAdvisorConfig.java  # 知识库配置
│   │   ├── LoveAppDocumentLoader.java         # 文档加载
│   │   └── QueryRewriter.java                 # 查询重写
│   ├── tools/                    # 工具集
│   │   ├── FileOperationTool.java    # 文件操作
│   │   ├── WebSearchTool.java        # 网络搜索
│   │   ├── WebScrapingTool.java      # 网页抓取
│   │   ├── PDFGenerationTool.java    # PDF 生成
│   │   └── TerminalOperationTool.java # 终端操作
│   ├── chatmemory/               # 对话记忆
│   │   └── FileBasedChatMemory.java
│   └── config/                   # 配置类
│       └── CorsConfig.java       # 跨域配置
├── src/main/resources/
│   ├── document/                 # 知识库文档
│   │   ├── 反诈常见问题和回答_老年篇.md
│   │   ├── 反诈常见问题和回答_青年篇.md
│   │   ├── 反诈常见问题和回答_少儿篇.md
│   │   ├── 反诈骗常见问题与回答_财会篇.md
│   │   └── 反诈骗常见问题与回答_自由职业者篇.md
│   └── application.yml           # 应用配置
├── yu-ai-agent-fronted/          # 前端项目
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatRoom.vue      # 聊天组件
│   │   ├── views/
│   │   │   ├── HomeView.vue      # 首页
│   │   │   ├── LoveAppView.vue   # 对话页
│   │   │   └── ManusView.vue     # Agent 页
│   │   └── api/
│   │       ├── http.js           # HTTP 请求
│   │       └── sse.js            # SSE 流式请求
│   └── package.json
└── yu-image-serch-mcp/           # MCP 图片搜索服务
```

## 快速开始

### 环境要求
- JDK 17+
- Node.js 18+
- Maven 3.6+

### 配置

1. 配置阿里云百炼 API Key（`application-local.yml`）：
```yaml
spring:
  ai:
    dashscope:
      api-key: your-api-key-here
```

2. 配置知识库索引名称：
```java
final String KNOWLEDGE_INDEX = "反诈大师";
```

### 启动后端

```bash
cd yu-ai-agent
mvn spring-boot:run
```

后端服务启动在 `http://localhost:8123/api`

### 启动前端

```bash
cd yu-ai-agent-fronted
npm install
npm run dev
```

前端服务启动在 `http://localhost:5173`

## API 接口

### 对话接口

```
GET /api/ai/love_app/chat/sse?message={message}&chatId={chatId}
```

SSE 流式返回 AI 回复。

### 图片识别接口

```
POST /api/ai/vision/analyze
Content-Type: application/json

{
  "imageBase64": "base64编码的图片数据",
  "prompt": "分析提示词"
}
```

### 健康检查

```
GET /api/health
```

## 核心特性

### 1. 视觉大模型图片识别
- 使用 qwen-vl-max 模型进行 OCR 文字提取
- 自动识别图片中的诈骗关键词
- 支持多种图片格式

### 2. 角色自动识别
- 根据用户语言风格自动判断角色
- 支持手动切换角色
- 角色记忆机制保持对话连贯

### 3. 风险评估
- 三级风险等级（低/中/高）
- 诈骗类型分类
- 安全建议生成

### 4. 性能优化
- 图片压缩传输
- 并行媒体识别
- Canvas 对象复用
- 静态常量优化

## 知识库

系统内置五大角色专属知识库：
- **老年篇**：针对老年人的常见诈骗类型（保健品诈骗、以房养老诈骗等）
- **青年篇**：针对青年的常见诈骗类型（刷单诈骗、杀猪盘等）
- **少儿篇**：针对少儿的常见诈骗类型（游戏充值诈骗、免费皮肤诈骗等）
- **财会篇**：针对财会人员的常见诈骗类型（冒充老板诈骗、虚假发票等）
- **自由职业者篇**：针对自由职业者的常见诈骗类型（兼职诈骗、虚假合作等）

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请提交 Issue 或联系项目维护者。
