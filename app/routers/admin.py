"""
管理与三元组抽取 API 路由
P1 阶段实现：文档解析、批量抽取、实体消歧、数据库管理
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import ExtractRequest, ExtractStats

router = APIRouter()


@router.post("/extract/start", summary="启动三元组抽取任务")
async def start_extraction(request: ExtractRequest, background_tasks: BackgroundTasks):
    """
    启动批量三元组抽取（后台任务）
    默认使用云端 GLM，支持断点续跑
    """
    # TODO P1: 后台调用 extract_triples.py 的抽取逻辑
    raise HTTPException(status_code=501, detail="P1 阶段实现")


@router.get("/extract/status", summary="抽取任务状态")
async def get_extraction_status():
    """查询当前抽取任务的进度和统计"""
    # TODO P1: 从抽取日志表读取进度
    raise HTTPException(status_code=501, detail="P1 阶段实现")


@router.post("/db/init", summary="初始化数据库")
async def init_database():
    """创建 SQLite 表结构，初始化空图谱"""
    # TODO P1: 执行 scripts/init_db.py 的逻辑
    raise HTTPException(status_code=501, detail="P1 阶段实现")


@router.get("/db/stats", summary="数据库统计")
async def get_db_stats():
    """返回文档数、实体数、三元组数等统计"""
    # TODO P1: 查询 SQLite 统计
    raise HTTPException(status_code=501, detail="P1 阶段实现")


@router.post("/db/rebuild", summary="重建图谱")
async def rebuild_graph():
    """清空现有三元组，从抽取结果重新构建 NetworkX 图"""
    # TODO P1: 清空后重新加载
    raise HTTPException(status_code=501, detail="P1 阶段实现")
