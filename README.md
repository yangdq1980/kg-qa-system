# 企业知识图谱与智能问答系统

基于三元组知识图谱与 RAG 深度融合的企业智能问答系统，面向压延膜制造业。

## 技术栈

- **后端**: FastAPI + Uvicorn
- **图计算**: NetworkX（内存图）+ SQLite（持久化）
- **前端**: HTML + ECharts（力导向图）
- **LLM**: 云端 GLM（三元组抽取）+ 本地 Ollama（实时问答）
- **向量检索**: 复用 enterprise-rag 的 FAISS/Chroma 向量库

## 项目结构

```
kg_qa_system/
├── app/
│   ├── main.py                  # FastAPI 入口
│   ├── routers/                 # API 路由
│   │   ├── graph.py             # 图谱接口（P2）
│   │   ├── search.py            # 搜索接口（P2）
│   │   ├── qa.py                # 问答接口（P3）
│   │   └── admin.py             # 管理/抽取接口（P1）
│   ├── services/                # 核心服务
│   │   ├── graph_service.py     # NetworkX 图服务
│   │   ├── rag_service.py       # RAG 向量检索
│   │   ├── entity_linker.py     # 实体链接
│   │   └── qa_pipeline.py       # 融合问答流水线
│   ├── models/schemas.py        # Pydantic 数据模型
│   └── static/                  # 前端静态文件
│       ├── index.html
│       ├── css/style.css
│       └── js/app.js
├── config/settings.py           # 全局配置
├── data/
│   ├── docs/                    # 原始文档（Word/MD）
│   ├── triples/                 # 抽取的三元组缓存
│   └── vector_store/            # 向量库（或软链接 enterprise-rag）
├── db/knowledge_graph.db        # SQLite 数据库
├── scripts/
│   ├── check_env.py             # 环境检查脚本
│   ├── init_db.py               # 数据库初始化
│   └── extract_triples.py       # 三元组批量抽取（P1）
├── tests/                       # 测试用例（P4）
├── requirements.txt
├── .env.example                 # 环境变量模板
├── .gitignore
└── README.md
```

## 快速开始（目标工作站）

### 1. 环境检查

```bash
# 进入项目目录
cd kg_qa_system

# 运行环境检查
python scripts/check_env.py
```

### 2. 安装依赖

```bash
# 建议使用虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制模板
cp .env.example .env
# 编辑 .env，填入 GLM_API_KEY、向量库路径、Ollama 模型名等
```

### 4. 初始化数据库

```bash
python scripts/init_db.py
```

### 5. 启动服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 查看前端页面  
访问 http://localhost:8000/docs 查看 API 文档  
访问 http://localhost:8000/health 检查各组件状态

## 开发阶段说明

| 阶段 | 状态 | 说明 |
|------|------|------|
| P0 环境与骨架 | ✅ 完成 | 项目结构、配置、健康检查、最小前端 |
| P1 数据抽取 | ⏳ 待开发 | 文档解析、GLM 三元组抽取、消歧、入库 |
| P2 图谱可视化 | ⏳ 待开发 | ECharts 力导向图、搜索、点击展开 |
| P3 融合问答 | ⏳ 待开发 | 实体链接、图谱+RAG融合、LLM生成、联动 |
| P4 优化与文档 | ⏳ 待开发 | 增量更新、性能优化、测试、部署手册 |

## 本体 Schema

### 实体类型（11类）
产品、原材料、配方、工艺、工序、设备、车间、工艺参数、质量指标、缺陷、岗位

### 关系类型（8类）
由组成、遵循工艺、包含工序、使用设备、位于、设定参数、检验指标、产生缺陷

详见 `需求建议书_v1.0.md`

## API 接口

| 方法 | 路径 | 说明 | 阶段 |
|------|------|------|------|
| GET | /health | 系统健康检查 | P0 |
| GET | /api/graph/full | 获取完整图谱 | P2 |
| POST | /api/graph/subgraph | 获取子图 | P2 |
| POST | /api/graph/path | 路径查询 | P2 |
| GET | /api/search/entities | 实体搜索 | P2 |
| POST | /api/qa/ask | 智能问答 | P3 |
| POST | /api/admin/extract/start | 启动抽取 | P1 |
| POST | /api/admin/db/init | 初始化数据库 | P1 |
