"""
全局配置文件
目标机器部署后，请根据实际环境修改以下配置，或在项目根目录创建 .env 文件覆盖。
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ===== 项目基础 =====
    PROJECT_NAME: str = "企业知识图谱与智能问答系统"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 项目根目录（config/settings.py 的上两级）
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # ===== 服务端口 =====
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ===== Ollama（本地 LLM，用于实时问答）=====
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_QA_MODEL: str = "deepseek-r1:7b"       # 问答用模型，按实际拉取的模型名修改
    OLLAMA_EMBED_MODEL: str = "bge-large:latest"  # 嵌入模型，需与 enterprise-rag 建库时一致

    # ===== 云端 GLM（用于批量三元组抽取）=====
    GLM_API_URL: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    GLM_API_KEY: str = ""                          # 填入你的 GLM API Key
    GLM_MODEL: str = "glm-4-plus"                 # 抽取用模型，质量优先

    # ===== 向量库（复用 enterprise-rag）=====
    # 如果 enterprise-rag 的向量库在其他位置，填写绝对路径
    VECTOR_STORE_PATH: str = ""
    VECTOR_STORE_TYPE: str = "faiss"              # faiss / chroma / other

    # ===== 图数据库 =====
    SQLITE_DB_PATH: str = "db/knowledge_graph.db"
    GRAPH_CACHE_PATH: str = "data/triples/graph_cache.json"

    # ===== 文档目录 =====
    DOCS_DIR: str = "data/docs"

    # ===== 本体 Schema（实体类型和关系类型枚举）=====
    ENTITY_TYPES: list = [
        "产品", "原材料", "配方", "工艺", "工序", "设备",
        "车间", "工艺参数", "质量指标", "缺陷", "岗位"
    ]
    RELATION_TYPES: list = [
        "由组成", "遵循工艺", "包含工序", "使用设备",
        "位于", "设定参数", "检验指标", "产生缺陷"
    ]

    # ===== 问答参数 =====
    QA_MAX_TOKENS: int = 1024
    QA_TEMPERATURE: float = 0.3
    RAG_TOP_K: int = 5
    GRAPH_SUBGRAPH_DEPTH: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
