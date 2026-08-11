"""
问答流水线：图谱检索 + RAG检索 + LLM生成 的深度融合
P3 阶段实现，是系统的核心
"""
import time
import requests
from typing import List, Dict, Tuple
from app.services.graph_service import graph_service
from app.services.rag_service import rag_service
from app.services.entity_linker import entity_linker
from app.models.schemas import QARequest, QAResponse, SourceItem
from config.settings import settings


class QAPipeline:
    """
    档次3 深度融合问答流水线
    流程：实体链接 → 图谱子图检索 → RAG向量检索 → 融合Prompt → LLM生成 → 高亮实体
    """

    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/chat"

    async def run(self, request: QARequest) -> QAResponse:
        """执行完整问答流水线"""
        start_time = time.time()
        highlighted_ids = []
        graph_triples = []
        sources = []

        # ① 实体链接
        linked_entities = []
        if request.use_graph:
            linked_entities = entity_linker.link(request.question)
            highlighted_ids = [e["id"] for e in linked_entities]

        # ② 图谱检索（精确结构化事实）
        graph_context = ""
        if request.use_graph and linked_entities:
            entity_ids = [e["id"] for e in linked_entities]
            nodes, edges = graph_service.get_subgraph(entity_ids, depth=settings.GRAPH_SUBGRAPH_DEPTH)
            graph_triples = self._edges_to_triples(nodes, edges)
            graph_context = self._format_graph_context(graph_triples)
            for t in graph_triples:
                sources.append(SourceItem(
                    type="graph",
                    content=f"{t['subject']} - {t['relation']} -> {t['object']}",
                    reference=t.get("source_doc", ""),
                    score=t.get("confidence", 1.0),
                ))

        # ③ RAG 检索（模糊描述性内容）
        rag_context = ""
        if request.use_rag:
            rag_results = rag_service.search(request.question, top_k=settings.RAG_TOP_K)
            rag_context = self._format_rag_context(rag_results)
            for r in rag_results:
                sources.append(SourceItem(
                    type="document",
                    content=r.get("content", ""),
                    reference=r.get("source", ""),
                    score=r.get("score", None),
                ))

        # ④ 融合 Prompt + LLM 生成
        answer = self._generate_answer(request.question, graph_context, rag_context)

        latency_ms = int((time.time() - start_time) * 1000)

        return QAResponse(
            answer=answer,
            sources=sources,
            highlighted_entity_ids=highlighted_ids,
            graph_triples=graph_triples,
            latency_ms=latency_ms,
        )

    def _edges_to_triples(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """将子图的边转换为可读三元组"""
        node_map = {n["id"]: n for n in nodes}
        triples = []
        for edge in edges:
            s = node_map.get(edge["source"], {}).get("name", edge["source"])
            o = node_map.get(edge["target"], {}).get("name", edge["target"])
            triples.append({
                "subject": s,
                "relation": edge.get("relation", ""),
                "object": o,
                "source_doc": edge.get("source_doc"),
                "confidence": edge.get("confidence", 1.0),
            })
        return triples

    def _format_graph_context(self, triples: List[Dict]) -> str:
        """将图谱三元组格式化为 Prompt 上下文"""
        if not triples:
            return ""
        lines = ["【来自知识图谱的结构化事实】"]
        for t in triples:
            lines.append(f"- {t['subject']} {t['relation']} {t['object']}")
        return "\n".join(lines)

    def _format_rag_context(self, results: List[Dict]) -> str:
        """将 RAG 检索结果格式化为 Prompt 上下文"""
        if not results:
            return ""
        lines = ["【来自文档库的参考内容】"]
        for i, r in enumerate(results, 1):
            src = r.get("source", "未知文档")
            lines.append(f"[{i}] 来源: {src}\n{r.get('content', '')}")
        return "\n".join(lines)

    def _generate_answer(self, question: str, graph_context: str, rag_context: str) -> str:
        """调用本地 Ollama 生成答案"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(question, graph_context, rag_context)

        try:
            resp = requests.post(
                self.ollama_url,
                json={
                    "model": settings.OLLAMA_QA_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {
                        "num_predict": settings.QA_MAX_TOKENS,
                        "temperature": settings.QA_TEMPERATURE,
                    },
                },
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json()["message"]["content"]
            return f"[LLM调用失败] HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            return f"[LLM调用异常] {str(e)}"

    def _build_system_prompt(self) -> str:
        """构建系统 Prompt"""
        return (
            "你是一个压延膜制造企业的知识助手。"
            "回答问题时，请优先使用【知识图谱的结构化事实】，"
            "【文档库的参考内容】作为补充和解释。"
            "如果两类信息都无法回答，请明确说明'知识库中暂无相关信息'，不要编造。"
            "回答中涉及的关键事实，请标注信息来源（图谱/文档名）。"
        )

    def _build_user_prompt(self, question: str, graph_context: str, rag_context: str) -> str:
        """构建用户 Prompt"""
        parts = [f"问题：{question}"]
        if graph_context:
            parts.append(graph_context)
        if rag_context:
            parts.append(rag_context)
        parts.append("请基于以上信息回答问题。")
        return "\n\n".join(parts)


# 全局单例
qa_pipeline = QAPipeline()
