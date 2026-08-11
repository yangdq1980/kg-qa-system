"""
FastAPI 应用入口
启动命令：uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import sys
import platform
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 确保项目根目录在 sys.path 中
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from app.models.schemas import HealthStatus
from app.routers import graph, search, qa, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化，关闭时清理"""
    # 启动：初始化图数据库、向量库连接等
    print(f"[启动] {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"[启动] 监听地址: http://{settings.HOST}:{settings.PORT}")
    yield
    # 关闭：释放资源
    print("[关闭] 正在释放资源...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于三元组知识图谱与RAG深度融合的企业智能问答系统",
    lifespan=lifespan,
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

# 注册路由
app.include_router(graph.router, prefix="/api/graph", tags=["知识图谱"])
app.include_router(search.router, prefix="/api/search", tags=["搜索"])
app.include_router(qa.router, prefix="/api/qa", tags=["智能问答"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理与抽取"])


@app.get("/", include_in_schema=False)
async def index():
    """首页：返回前端页面"""
    index_path = BASE_DIR / "app" / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": f"{settings.PROJECT_NAME} 运行中，请访问 /docs 查看API文档"}


@app.get("/health", response_model=HealthStatus, tags=["系统"])
async def health_check():
    """
    健康检查接口
    返回各依赖组件的连通状态，用于 P0 验证和后续运维监控
    """
    import requests

    status = HealthStatus(
        version=settings.VERSION,
        python_version=platform.python_version(),
    )

    # 检查 Ollama
    try:
        resp = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            status.ollama = {"status": "ok", "models": models}
        else:
            status.ollama = {"status": "error", "message": f"HTTP {resp.status_code}"}
    except Exception as e:
        status.ollama = {"status": "unreachable", "message": str(e)}

    # 检查 GLM API（仅检查 Key 是否配置，不实际调用以免消耗额度）
    if settings.GLM_API_KEY:
        status.glm_api = {"status": "configured", "model": settings.GLM_MODEL}
    else:
        status.glm_api = {"status": "not_configured", "message": "GLM_API_KEY 未设置，三元组抽取将不可用"}

    # 检查向量库
    vector_path = Path(settings.VECTOR_STORE_PATH) if settings.VECTOR_STORE_PATH else BASE_DIR / settings.VECTOR_STORE_TYPE
    if vector_path.exists():
        status.vector_store = {"status": "ok", "path": str(vector_path), "type": settings.VECTOR_STORE_TYPE}
    else:
        status.vector_store = {"status": "not_found", "path": str(vector_path), "message": "向量库路径不存在，问答RAG部分将不可用"}

    # 检查图数据库
    db_path = BASE_DIR / settings.SQLITE_DB_PATH
    if db_path.exists():
        status.graph_db = {"status": "ok", "path": str(db_path)}
    else:
        status.graph_db = {"status": "not_initialized", "path": str(db_path), "message": "数据库未初始化，请运行 scripts/init_db.py"}

    # 总体状态
    all_ok = all(
        component.get("status") in ("ok", "configured")
        for component in [status.ollama, status.glm_api, status.vector_store, status.graph_db]
    )
    status.status = "ok" if all_ok else "degraded"

    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
