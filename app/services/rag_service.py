"""
RAG 服务：复用 enterprise-rag 的向量库进行文档检索
P3 阶段实现，需确认 enterprise-rag 的向量库格式和嵌入模型
"""
from typing import List, Dict, Optional
from config.settings import settings


class RAGService:
    """向量检索服务，对接 enterprise-rag 已有的向量库"""

    def __init__(self):
        self.vector_store = None
        self.embed_model = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        初始化向量库连接
        返回 True 表示初始化成功，False 表示向量库不可用
        """
        # TODO P3: 根据 VECTOR_STORE_TYPE 加载对应的向量库
        # - FAISS: 加载 index.faiss + index.pkl
        # - Chroma: PersistentClient
        # 嵌入模型必须与建库时一致（settings.OLLAMA_EMBED_MODEL）
        self._initialized = False
        return False

    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        向量检索相关文档片段
        返回格式: [{"content": "...", "source": "文档名", "score": 0.92, "page": 1}]
        """
        if not self._initialized:
            return []
        # TODO P3: 调用嵌入模型生成 query 向量，检索 top_k
        top_k = top_k or settings.RAG_TOP_K
        return []

    def get_doc_count(self) -> int:
        """返回向量库中的文档片段数量"""
        # TODO P3: 查询向量库大小
        return 0

    def get_available_collections(self) -> List[str]:
        """返回可用的集合/索引列表"""
        # TODO P3
        return []


# 全局单例
rag_service = RAGService()
