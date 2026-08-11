"""
智能问答 API 路由
P3 阶段实现：图谱+RAG深度融合问答
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import QARequest, QAResponse

router = APIRouter()


@router.post("/ask", response_model=QAResponse, summary="智能问答")
async def ask_question(request: QARequest):
    """
    核心问答接口
    流程：实体链接 → 图谱子图检索 → RAG向量检索 → 融合Prompt → LLM生成 → 高亮实体
    """
    # TODO P3: 调用 QAPipeline.run()
    raise HTTPException(status_code=501, detail="P3 阶段实现")


@router.post("/ask/stream", summary="流式问答（SSE）")
async def ask_question_stream(request: QARequest):
    """
    流式返回答案（Server-Sent Events）
    提升长答案的用户体验
    """
    # TODO P3: 使用 StreamingResponse + Ollama stream 模式
    raise HTTPException(status_code=501, detail="P3 阶段实现")


@router.get("/history", summary="问答历史")
async def get_history(limit: int = 20):
    """获取历史问答记录（本地存储，个人使用）"""
    # TODO P3: 从 SQLite 或 JSON 文件读取历史
    raise HTTPException(status_code=501, detail="P3 阶段实现")
