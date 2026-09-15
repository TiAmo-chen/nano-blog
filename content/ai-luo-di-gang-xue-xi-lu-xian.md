---
title: LangChain 学习
date: 2026-04-20
tags: [AI, 学习路线, LangChain, RAG, LLM, Python]
slug: ai-luo-di-gang-xue-xi-lu-xian
---
## 📚 课程推荐

### 免费课程（优先推荐）

| 课程 | 平台 | 时长 | 说明 |
|------|------|------|------|
| **LangChain for LLM Application Development** | DeepLearning.AI | 2 小时 | 吴恩达出品，入门首选 |
| **RAG Fundamentals** | DeepLearning.AI | 1 小时 | RAG 基础概念 |
| **Building Systems with LLMs** | DeepLearning.AI | 3 小时 | 系统设计与评估 |
| **LangChain 官方文档** | langchain.com | 自学 | 最新最权威 |

### 中文课程

| 课程 | 平台 | 特点 |
|------|------|------|
| **AI 大模型应用开发实战训练营** | 知乎课堂 | 项目驱动，有社群 |
| **李宏毅 LLM 课程** | YouTube/B 站 | 理论深入，免费 |
| **RAG 从入门到实战** | B 站/知乎 | 实战导向 |

---

## 🗺️ 学习路线（3-6 个月）

### 第 1 阶段：Python 基础（2-4 周）

```
✅ 目标：能独立写 Python 脚本
├── Python 语法基础
├── 面向对象编程
├── 异步编程 (asyncio)
├── 常用库：requests, json, pathlib
└── 项目：写一个爬虫或数据处理脚本
```

**推荐资源：**
- 《Python 编程：从入门到实践》
- B 站：小甲鱼 Python 教程

---

### 第 2 阶段：LLM 基础（2-3 周）

```
✅ 目标：理解 LLM 原理，会调用 API
├── Transformer 基础概念
├── Prompt Engineering
├── 主流 API 使用 (OpenAI/Claude/通义/DeepSeek)
├── Token 计算与成本优化
└── 项目：用 API 做一个聊天机器人
```

**核心知识点：**
- Temperature/Top-p 参数调节
- System/User/Assistant 消息结构
- 流式输出 (streaming)
- 错误处理与重试

---

### 第 3 阶段：LangChain 框架（3-4 周）

```
✅ 目标：能用 LangChain 构建应用
├── ChatModel / LLM 调用
├── Prompt Template
├── Chain 链式调用
├── Memory 上下文管理
├── Document Loader
├── Text Splitter
├── Embedding & VectorStore
├── Retriever
└── 项目：文档问答系统
```

**LangChain 核心模块：**
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
```

---

### 第 4 阶段：RAG 实战（4-6 周）

```
✅ 目标：能搭建生产级 RAG 系统
├── 文档解析 (PDF/Word/Markdown)
├── 文本分块策略
├── Embedding 模型选择
├── 向量数据库 (Chroma/Milvus)
├── 检索优化 (混合检索/重排序)
├── 幻觉处理
├── 效果评估
└── 项目：企业知识库问答系统
```

---

### 第 5 阶段：工程化（4-6 周）

```
✅ 目标：能部署上线
├── FastAPI 开发
├── Docker 容器化
├── 并发处理
├── 日志监控
├── 性能优化
└── 项目：完整上线一个 RAG 应用
```

---

## 🔨 完整 RAG 项目推荐

### 项目：企业知识库问答系统

**场景**：公司有大量产品文档/手册，客服需要快速查找答案

---

### 技术栈

```
┌─────────────────────────────────────────┐
│              前端 (可选)                  │
│           Streamlit / Vue               │
├─────────────────────────────────────────┤
│              后端 API                     │
│           FastAPI + Uvicorn             │
├─────────────────────────────────────────┤
│           RAG 核心逻辑                    │
│    LangChain + Chroma + DeepSeek        │
├─────────────────────────────────────────┤
│              数据存储                     │
│    向量库：Chroma / 文件：本地/云存储    │
└─────────────────────────────────────────┘
```

---

### 项目结构

```
rag-kb-bot/
├── data/                    # 知识库文档
│   ├── products/           # 产品手册
│   ├── faq/               # 常见问题
│   └── policies/          # 政策文档
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置
│   ├── loader.py          # 文档加载
│   ├── splitter.py        # 文本分块
│   ├── embedding.py       # 向量化
│   ├── retriever.py       # 检索
│   ├── generator.py       # 答案生成
│   └── api.py            # FastAPI 接口
├── vectorstore/           # 向量数据库
├── tests/                 # 测试
├── requirements.txt
├── Dockerfile
└── README.md
```

---

### 核心代码示例

#### 1️⃣ 文档加载与分块

```python
# src/loader.py
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_documents(data_dir: str):
    """加载指定目录下的所有文档"""
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """文本分块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"分块完成：{len(chunks)} 个 chunks")
    return chunks
```

#### 2️⃣ 向量化与存储

```python
# src/embedding.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

def create_vectorstore(chunks, persist_dir="./vectorstore"):
    """创建向量数据库"""
    # 使用 DeepSeek 或其他兼容 API
    embeddings = OpenAIEmbeddings(
        openai_api_key="sk-xxx",
        openai_api_base="https://api.deepseek.com/v1",
        model="deepseek-embed"
    )
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectorstore
```

#### 3️⃣ 检索与生成

```python
# src/retriever.py
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

def create_rag_chain(vectorstore, model_name="deepseek-chat"):
    """创建 RAG 问答链"""
    llm = ChatOpenAI(
        openai_api_key="sk-xxx",
        openai_api_base="https://api.deepseek.com/v1",
        model=model_name,
        temperature=0.3  # 降低幻觉
    )
    
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,              # 返回 5 个最相关文档
            "score_threshold": 0.7  # 相似度阈值
        }
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": create_prompt()
        }
    )
    return qa_chain

def create_prompt():
    """自定义 Prompt"""
    from langchain.prompts import PromptTemplate
    
    template = """你是一个专业的客服助手。请根据以下参考信息回答问题。
如果参考信息中没有答案，请直接说"抱歉，我没有找到相关信息"。
回答时请注明信息来源。

参考信息：
{context}

问题：{question}
回答："""
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
```

#### 4️⃣ API 接口

```python
# src/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .retriever import create_rag_chain

app = FastAPI()

class Question(BaseModel):
    question: str
    top_k: int = 5

class Answer(BaseModel):
    answer: str
    sources: list[str]

@app.post("/ask", response_model=Answer)
async def ask_question(q: Question):
    try:
        result = qa_chain({"query": q.question})
        sources = [doc.page_content for doc in result["source_documents"]]
        return Answer(
            answer=result["result"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 5️⃣ 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建并运行
docker build -t rag-kb-bot .
docker run -p 8000:8000 rag-kb-bot
```

---

## 📋 项目进阶优化

| 优化方向 | 具体做法 |
|---------|---------|
| **检索优化** | 混合检索 (BM25+ 向量)、Query 改写、多路召回 |
| **分块优化** | 按语义分块、父子文档检索 |
| **重排序** | 用 Cross-Encoder 对检索结果重排序 |
| **缓存** | Redis 缓存相似问题答案 |
| **监控** | 记录用户反馈、bad case 分析 |
| **评估** | 构建测试集，计算准确率/召回率 |

---

## 🎯 学习建议

1. **先跑通再优化**：第一个项目不要追求完美，先让系统跑起来
2. **记录踩坑过程**：这些都是面试时的谈资
3. **部署上线**：哪怕只是本地运行，也比只跑过 Demo 强
4. **写技术博客**：总结学习过程，建立个人品牌
5. **参与开源**：给 LangChain 等提 PR 或写文档

---

## 📦 快速开始命令

```bash
# 1. 创建项目
mkdir rag-kb-bot && cd rag-kb-bot
python -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install langchain langchain-community chromadb fastapi uvicorn pypdf

# 3. 准备数据
mkdir -p data/products
# 放入一些 PDF 文档

# 4. 运行
python src/loader.py
python src/api.py
```
