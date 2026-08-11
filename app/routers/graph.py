"""
知识图谱 API 路由
P2 阶段实现：子图查询、路径查询、全图数据返回、布局计算
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import GraphData, SubgraphRequest, PathRequest

router = APIRouter()


@router.get("/full", response_model=GraphData, summary="获取完整图谱")
async def get_full_graph(limit: int = 2000):
    """
    获取完整图谱数据（节点+边），用于 ECharts 渲染
    limit: 节点数量上限，防止浏览器卡死
    """
    # TODO P2: 调用 GraphService 获取全图，计算布局坐标
    raise HTTPException(status_code=501, detail="P2 阶段实现")


@router.post("/subgraph", response_model=GraphData, summary="获取子图")
async def get_subgraph(request: SubgraphRequest):
    """
    根据中心实体ID获取指定深度的子图
    用于点击节点展开邻接节点
    """
    # TODO P2: 调用 GraphService.neighbors() 获取子图
    raise HTTPException(status_code=501, detail="P2 阶段实现")


@router.post("/path", summary="查询两节点间路径")
async def get_path(request: PathRequest):
    """
    查询两个实体之间的关系路径
    用于回答"A和B什么关系"类问题
    """
    # TODO P2: 调用 NetworkX shortest_path / all_simple_paths
    raise HTTPException(status_code=501, detail="P2 阶段实现")


@router.get("/stats", summary="图谱统计信息")
async def get_graph_stats():
    """返回实体数量、关系数量、各类型分布等统计"""
    # TODO P2: 统计 NetworkX 图的节点和边
    raise HTTPException(status_code=501, detail="P2 阶段实现")
