"""
实体链接服务：将用户问题中的自然语言表述匹配到图谱节点
P3 阶段实现，是档次3问答的关键环节
"""
from typing import List, Dict, Tuple, Optional
from app.services.graph_service import graph_service
from config.settings import settings


class EntityLinker:
    """
    实体链接器
    输入：用户问题文本
    输出：匹配到的图谱节点ID列表（带置信度）
    """

    def __init__(self):
        self.alias_map: Dict[str, str] = {}  # 别名 -> 节点ID
        self._build_alias_index()

    def _build_alias_index(self) -> None:
        """构建别名索引（从图谱节点的名称和别名）"""
        # TODO P3: 遍历所有节点，建立 名称/别名 -> node_id 的映射
        # 支持简称、全称、英文缩写等
        pass

    def link(self, question: str) -> List[Dict]:
        """
        从问题中识别并链接到图谱实体
        返回: [{"id": "...", "name": "...", "type": "...", "confidence": 0.95, "span": (start, end)}]
        """
        results = []
        # TODO P3: 实现实体链接
        # 策略1：词典匹配（遍历所有节点名和别名，检查是否出现在问题中）
        # 策略2：LLM 辅助（让本地模型从问题中提取实体，再匹配图谱）
        # 策略3：混合（词典匹配优先，LLM 补充）
        return results

    def link_with_llm(self, question: str) -> List[Dict]:
        """使用本地 LLM 辅助实体链接（准确率更高但更慢）"""
        # TODO P3: 构造 Prompt，让 LLM 从问题中提取实体名和类型，再匹配图谱
        return []

    def normalize_entity_name(self, name: str) -> str:
        """实体名标准化（去空格、统一大小写、全半角转换等）"""
        return name.strip().lower()

    def fuzzy_match(self, name: str, threshold: float = 0.7) -> Optional[Dict]:
        """
        模糊匹配一个实体名到图谱节点
        使用编辑距离或序列相似度
        """
        # TODO P3: difflib.SequenceMatcher 或 rapidfuzz
        return None


# 全局单例
entity_linker = EntityLinker()
