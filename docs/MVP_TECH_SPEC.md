# AI Reading Companion - MVP 技术方案

## 1. MVP目标

实现：

输入书名

↓

输出讲书稿

---

不实现：

音频

实时对话

打断机制

长期记忆

---

## 2. 技术架构

Frontend

↓

Generate API

↓

Content Orchestrator

↓

LLM

↓

Output

---

推荐技术栈：

Frontend：

* Next.js 15+
* React 19
* TypeScript

Backend：

* Next.js API Route

Model：

* OpenAI API（推荐 GPT-4.1 或 GPT-4o）

Storage：

* 本地文件（开发阶段）
* SQLite（可选）

---

## 3. 开发环境依赖清单

### 必装软件

#### Node.js

推荐版本：

```bash
v20.x LTS
```

检查版本：

```bash
node -v
npm -v
```

---

#### Git

检查版本：

```bash
git --version
```

---

#### VS Code

推荐插件：

* ESLint
* Prettier
* Tailwind CSS IntelliSense
* GitLens

---

## 4. 项目依赖安装

初始化项目：

```bash
npx create-next-app@latest ai-reading-companion --typescript --app
```

进入项目：

```bash
cd ai-reading-companion
```

---

### 核心依赖

#### OpenAI SDK

```bash
npm install openai
```

用于调用大模型。

---

#### Zod

```bash
npm install zod
```

用于：

* 数据结构校验
* LLM输出格式校验

---

#### dotenv

如果需要单独加载环境变量：

```bash
npm install dotenv
```

Next.js 通常已支持 `.env.local`。

---

### 开发依赖

```bash
npm install -D prettier eslint
```

---

## 5. 环境变量

创建：

```bash
.env.local
```

内容：

```env
OPENAI_API_KEY=your_api_key
```

---

## 6. 核心生成流程

### Step1

作品画像生成

输入：

书名

输出：

作品画像

---

结构：

Book Profile

* 作者
* 类型
* 故事原型
* 情感承诺
* 核心主线
* 核心人物
* 关键场景

---

示例：

倚天屠龙记

故事原型：

少年救世主神话

情感承诺：

拥有力量以后如何使用力量

---

### Step2

讲述骨架生成

输入：

作品画像

输出：

Narrative Outline

---

示例：

节点1

父母之死

节点2

寒毒与绝境

节点3

九阳神功

节点4

光明顶

节点5

成为教主

节点6

爱情与选择

节点7

离开权力中心

---

### Step3

节点内容生成

输入：

单个节点

输出：

节点正文

---

要求：

场景

因果

情绪

推进

---

禁止：

摘要

概括

主题先行

---

### Step4

内容拼接

节点正文

↓

完整讲述稿

---

### Step5

质量审查

使用第二次 LLM 调用。

---

检查项：

是否流水账

是否缺少场景

是否因果断裂

是否提前升华

是否人物动机模糊

是否缺少情绪推进

---

输出：

Quality Report

---

## 7. Prompt架构

禁止：

书名

↓

直接生成全文

---

必须：

书名

↓

作品画像

↓

讲述骨架

↓

节点生成

↓

质量审查

↓

最终稿

---

## 8. API设计

POST

```http
/api/generate
```

Request

```json
{
  "bookName": "倚天屠龙记"
}
```

Response

```json
{
  "profile": {},
  "outline": [],
  "content": "",
  "quality": {}
}
```

---

## 9. 目录结构

```text
src/
├── app/
│   └── api/
│       └── generate/
│           └── route.ts
│
├── lib/
│   ├── prompts/
│   │   ├── profile.ts
│   │   ├── outline.ts
│   │   ├── node.ts
│   │   └── review.ts
│   │
│   ├── orchestrator.ts
│   └── types.ts
│
docs/
├── MVP_PRD.md
└── MVP_TECH_SPEC.md
```

---

## 10. 第一阶段开发任务

优先实现：

### BookProfileGenerator

输入：

```text
书名
```

输出：

```json
{
  "title": "",
  "author": "",
  "genre": "",
  "archetype": "",
  "emotionalPromise": "",
  "mainTheme": "",
  "characters": [],
  "keyScenes": []
}
```

---

### OutlineGenerator

输入：

Book Profile

输出：

Narrative Outline

---

### NodeContentGenerator

输入：

单个节点

输出：

节点讲述内容

---

### QualityReviewer

输入：

完整讲书稿

输出：

质量评估报告

---

### ContentOrchestrator

负责：

```text
书名
↓
作品画像
↓
讲述骨架
↓
节点生成
↓
质量审查
↓
最终结果
```

---

## 11. 启动项目

开发模式：

```bash
npm run dev
```

访问：

```text
http://localhost:3000
```

---

## 12. 下一阶段

V0.5

新增：

TTS生成

目标：

验证听书体验

保持内容引擎不变

仅新增音频层

---

## 当前阶段建议

为了尽快验证内容引擎，不建议引入：

* 数据库
* Redis
* 向量数据库
* LangChain
* RAG
* 用户系统
* 登录鉴权
* 消息队列

当前只需要：

```text
Node.js
Next.js
TypeScript
OpenAI SDK
Zod
```

即可完成 MVP 开发。
