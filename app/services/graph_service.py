"""
图服务：NetworkX 图的加载、查询、布局计算
P1 阶段实现加载与持久化，P2 阶段实现查询与布局
"""
import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from config.settings import settings


class GraphService:
    """知识图谱服务，基于 NetworkX 有向图"""

    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()
        self._loaded = False

    def load(self) -> None:
        """从 SQLite 或缓存文件加载图谱到内存"""
        # TODO P1: 从 SQLite 读取三元组，构建 NetworkX 图
        # 优先加载 JSON 缓存，没有则从 SQLite 构建
        cache_path = Path(settings.GRAPH_CACHE_PATH)
        if cache_path.exists():
            self._load_from_cache(cache_path)
        else:
            self._loaded = True  # 空图

    def _load_from_cache(self, cache_path: Path) -> None:
        """从 JSON 缓存加载图"""
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for node in data.get("nodes", []):
            self.graph.add_node(node["id"], **node)
        for edge in data.get("edges", []):
            self.graph.add_edge(edge["source"], edge["target"], **edge)
        self._loaded = True

    def save_cache(self) -> None:
        """将当前图保存为 JSON 缓存"""
        # TODO P1: 序列化 NetworkX 图为 JSON
        pass

    def add_triple(self, subject_id: str, subject_name: str, subject_type: str,
                   relation: str, object_id: str, object_name: str, object_type: str,
                   source_doc: str = None, confidence: float = 1.0) -> None:
        """添加一条三元组到图中"""
        # TODO P1: 添加节点（带属性）和边
        pass

    def get_node(self, node_id: str) -> Optional[Dict]:
        """获取节点详情"""
        if node_id in self.graph.nodes:
            return dict(self.graph.nodes[node_id])
        return None

    def search_entities(self, keyword: str, entity_type: str = None, limit: int = 20) -> List[Dict]:
        """模糊搜索实体"""
        # TODO P2: 名称包含匹配 + 别名匹配 + 类型筛选
        results = []
        keyword_lower = keyword.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            name = attrs.get("name", "")
            aliases = attrs.get("aliases", [])
            if keyword_lower in name.lower() or any(keyword_lower in a.lower() for a in aliases):
                if entity_type is None or attrs.get("type") == entity_type:
                    results.append({
                        "id": node_id,
                        "name": name,
                        "type": attrs.get("type", ""),
                        "match_score": 1.0 if keyword_lower == name.lower() else 0.8,
                    })
                    if len(results) >= limit:
                        break
        return results

    def get_subgraph(self, entity_ids: List[str], depth: int = 2) -> Tuple[List[Dict], List[Dict]]:
        """获取以指定实体为中心的子图"""
        # TODO P2: BFS 遍历 depth 度，返回节点和边
        nodes = []
        edges = []
        visited = set()
        for eid in entity_ids:
            if eid in self.graph.nodes:
                visited.add(eid)
        # 简化版：只返回中心节点，P2 实现完整 BFS
        for nid in visited:
            nodes.append({"id": nid, **self.graph.nodes[nid]})
        return nodes, edges

    def get_paths(self, source_id: str, target_id: str, max_depth: int = 4) -> List[List[str]]:
        """查询两节点间的所有简单路径（限深度）"""
        # TODO P2: nx.all_simple_paths
        if source_id not in self.graph.nodes or target_id not in self.graph.nodes:
            return []
        try:
            paths = list(nx.all_simple_paths(self.graph, source_id, target_id, cutoff=max_depth))
            return paths
        except nx.NetworkXNoPath:
            return []

    def compute_layout(self, layout_type: str = "spring") -> Dict[str, Tuple[float, float]]:
        """计算图布局坐标"""
        # TODO P2: spring_layout / circular_layout / kamada_kawai_layout
        if layout_type == "spring":
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        elif layout_type == "circular":
            pos = nx.circular_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph, seed=42)
        return {nid: (float(x), float(y)) for nid, (x, y) in pos.items()}

    def get_stats(self) -> Dict:
        """返回图谱统计信息"""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "entity_types": {},  # TODO P1: 按类型统计
            "relation_types": {},  # TODO P1: 按关系统计
        }


# 全局单例
graph_service = GraphService()
