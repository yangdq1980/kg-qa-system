"""
Pydantic 数据模型定义
所有 API 请求/响应的数据结构在此统一管理
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ===== 图谱相关 =====

class EntityType(str, Enum):
    产品 = "产品"
    原材料 = "原材料"
    配方 = "配方"
    工艺 = "工艺"
    工序 = "工序"
    设备 = "设备"
    车间 = "车间"
    工艺参数 = "工艺参数"
    质量指标 = "质量指标"
    缺陷 = "缺陷"
    岗位 = "岗位"


class RelationType(str, Enum):
    由组成 = "由组成"
    遵循工艺 = "遵循工艺"
    包含工序 = "包含工序"
    使用设备 = "使用设备"
    位于 = "位于"
    设定参数 = "设定参数"
    检验指标 = "检验指标"
    产生缺陷 = "产生缺陷"


class GraphNode(BaseModel):
    """图谱节点"""
    id: str = Field(..., description="节点唯一ID")
    name: str = Field(..., description="实体名称")
    type: str = Field(..., description="实体类型")
    aliases: List[str] = Field(default_factory=list, description="别名列表")
    source_docs: List[str] = Field(default_factory=list, description="来源文档")
    properties: Dict[str, Any] = Field(default_factory=dict, description="扩展属性")


class GraphEdge(BaseModel):
    """图谱边（关系）"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    relation: str = Field(..., description="关系类型")
    source_doc: Optional[str] = Field(None, description="来源文档")
    confidence: float = Field(1.0, description="置信度 0-1")


class GraphData(BaseModel):
    """完整图谱数据（用于ECharts渲染）"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    stats: Dict[str, Any] = Field(default_factory=dict)


class SubgraphRequest(BaseModel):
    """子图查询请求"""
    entity_ids: List[str] = Field(..., description="中心实体ID列表")
    depth: int = Field(2, ge=1, le=4, description="展开深度")


class PathRequest(BaseModel):
    """路径查询请求"""
    source_id: str
    target_id: str
    max_depth: int = Field(4, ge=1, le=6)


# ===== 搜索相关 =====

class SearchResult(BaseModel):
    """实体搜索结果"""
    id: str
    name: str
    type: str
    match_score: float
    summary: Optional[str] = None


# ===== 问答相关 =====

class QARequest(BaseModel):
    """问答请求"""
    question: str = Field(..., description="用户问题")
    use_graph: bool = Field(True, description="是否使用图谱增强")
    use_rag: bool = Field(True, description="是否使用RAG检索")


class SourceItem(BaseModel):
    """答案来源"""
    type: str = Field(..., description="来源类型：graph / document")
    content: str = Field(..., description="来源内容")
    reference: Optional[str] = Field(None, description="引用标识（文档名/三元组）")
    score: Optional[float] = Field(None, description="相关度/置信度")


class QAResponse(BaseModel):
    """问答响应"""
    answer: str = Field(..., description="生成的答案")
    sources: List[SourceItem] = Field(default_factory=list)
    highlighted_entity_ids: List[str] = Field(default_factory=list, description="图谱中需高亮的节点ID")
    graph_triples: List[Dict[str, str]] = Field(default_factory=list, description="用到的图谱三元组")
    latency_ms: int = Field(0, description="响应耗时（毫秒）")


# ===== 管理/抽取相关 =====

class ExtractRequest(BaseModel):
    """三元组抽取请求"""
    doc_paths: Optional[List[str]] = Field(None, description="指定文档路径，为空则处理全部")
    use_cloud_glm: bool = Field(True, description="是否使用云端GLM抽取")
    skip_extracted: bool = Field(True, description="跳过已抽取的文档")


class ExtractStats(BaseModel):
    """抽取统计"""
    total_docs: int = 0
    processed_docs: int = 0
    skipped_docs: int = 0
    failed_docs: int = 0
    total_entities: int = 0
    total_relations: int = 0
    duration_seconds: float = 0.0


# ===== 健康检查 =====

class HealthStatus(BaseModel):
    """系统健康状态"""
    status: str = "ok"
    version: str
    python_version: str
    ollama: Dict[str, Any] = Field(default_factory=dict)
    glm_api: Dict[str, Any] = Field(default_factory=dict)
    vector_store: Dict[str, Any] = Field(default_factory=dict)
    graph_db: Dict[str, Any] = Field(default_factory=dict)
