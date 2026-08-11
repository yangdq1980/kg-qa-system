"""
搜索 API 路由
P2 阶段实现：实体模糊搜索、类型筛选搜索
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.schemas import SearchResult

router = APIRouter()


@router.get("/entities", response_model=List[SearchResult], summary="实体搜索")
async def search_entities(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    entity_type: str = Query(None, description="按实体类型筛选"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    模糊搜索图谱中的实体
    用于前端搜索框的自动补全和定位
    """
    # TODO P2: 调用 GraphService.search_entities()
    raise HTTPException(status_code=501, detail="P2 阶段实现")


@router.get("/suggest", summary="搜索建议")
async def search_suggest(
    prefix: str = Query(..., min_length=1, description="输入前缀"),
    limit: int = Query(10, ge=1, le=20),
):
    """输入时实时返回匹配的实体名建议"""
    # TODO P2: 前缀匹配 + 频率排序
    raise HTTPException(status_code=501, detail="P2 阶段实现")
