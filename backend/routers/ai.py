"""
AI 助手 API 路由 - LangChain 0.2.x 兼容版本
提供新闻总结和聊天的 REST API + 流式 SSE 接口
"""

import uuid
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news as news_crud
from agents.news_agent import get_news_agent

router = APIRouter(prefix="/api/ai", tags=['AI助手'])


# ==================== 请求/响应模型 ====================

class SummarizeRequest(BaseModel):
    """新闻总结请求"""
    news_id: int
    session_id: Optional[str] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: str
    news_id: Optional[int] = None
    news_summary: Optional[str] = None
    news_content: Optional[str] = None
    news_title: Optional[str] = None


class ClearHistoryRequest(BaseModel):
    """清除历史请求"""
    session_id: str


# ==================== 新闻总结 API ====================

@router.post("/summarize")
async def summarize_news(
    request: SummarizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    总结指定新闻内容（非流式版本）

    返回结构化的总结结果，包含关键点提取。
    """
    news_detail = await news_crud.get_news_detail(db, request.news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    session_id = request.session_id or str(uuid.uuid4())
    agent = get_news_agent(session_id)

    result = await agent.summarize_news(
        news_content=news_detail.content,
        news_title=news_detail.title,
        news_id=news_detail.id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=f"总结失败: {result.get('error')}")

    return {
        "code": 200,
        "message": "总结生成成功",
        "data": {
            "session_id": session_id,
            "news_id": news_detail.id,
            "title": news_detail.title,
            "summary": result["summary"],
            "key_points": result.get("key_points", []),
        }
    }


@router.post("/summarize/stream")
async def summarize_news_stream(
    request: SummarizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    流式总结新闻内容（Server-Sent Events）

    实时返回 AI 生成的每个 token，打字机效果。

    返回格式：
    event: start
    data: {"type": "start", "session_id": "..."}

    event: token
    data: {"type": "token", "content": "某"}

    event: token
    data: {"type": "token", "content": "个"}

    event: end
    data: {"type": "end", "summary": "...", "key_points": [...]}
    """
    news_detail = await news_crud.get_news_detail(db, request.news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    session_id = request.session_id or str(uuid.uuid4())
    agent = get_news_agent(session_id)

    async def event_generator():
        """SSE 事件生成器"""
        # 发送开始信号
        yield f"event: start\ndata: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"

        try:
            # 使用 LangChain 最新 astream API 流式收集
            streaming_chain = agent.summary_prompt | agent.streaming_llm
            input_data = {
                "news_content": f"标题：{news_detail.title}\n\n内容：{news_detail.content}"
            }

            full_response = []
            async for chunk in streaming_chain.astream(input_data):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response.append(token)
                yield f"event: token\ndata: {json.dumps({'type': 'token', 'content': token})}\n\n"

            # 发送结束信号
            summary_text = "".join(full_response)
            key_points = agent._extract_key_points(summary_text)

            # 更新 Agent 历史
            agent.conversation_history = [
                {"role": "system", "content": f"新闻标题：{news_detail.title}"},
                {"role": "assistant", "content": summary_text},
            ]

            end_data = {
                'type': 'end',
                'summary': summary_text,
                'key_points': key_points,
                'session_id': session_id,
            }
            yield f"event: end\ndata: {json.dumps(end_data)}\n\n"

        except Exception as e:
            error_msg = str(e)
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==================== 聊天 API ====================

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送聊天消息（非流式版本）"""
    agent = get_news_agent(request.session_id)

    news_content = request.news_content
    news_title = request.news_title

    if request.news_id and not news_content:
        news_detail = await news_crud.get_news_detail(db, request.news_id)
        if news_detail:
            news_content = news_detail.content
            news_title = news_detail.title

    result = await agent.chat(
        user_input=request.message,
        news_summary=request.news_summary,
        news_content=news_content,
        news_title=news_title or "",
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=f"对话失败: {result.get('error')}")

    return {
        "code": 200,
        "message": "对话成功",
        "data": {
            "response": result["response"],
            "chat_history": result.get("chat_history", []),
        }
    }


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式聊天（Server-Sent Events）

    实时返回 AI 回复的每个 token，支持多轮对话上下文。

    返回格式：
    event: start
    data: {"type": "start"}

    event: token
    data: {"type": "token", "content": "您"}

    event: end
    data: {"type": "end", "response": "您的回复内容..."}
    """
    agent = get_news_agent(request.session_id)

    news_content = request.news_content
    news_title = request.news_title

    # 如果提供了 news_id，获取新闻内容
    if request.news_id and not news_content:
        # 需要同步获取（这里简化处理，实际可在 Agent 中处理）
        pass

    async def event_generator():
        """SSE 事件生成器"""
        yield f"event: start\ndata: {json.dumps({'type': 'start'})}\n\n"

        try:
            # 构建聊天历史
            chat_history = agent._build_chat_history()

            # 构建输入
            if request.news_summary:
                prompt_input = {
                    "user_input": f"参考以下新闻内容回答：\n\n{request.news_summary}\n\n用户问题：{request.message}",
                    "chat_history": chat_history,
                }
                streaming_chain = agent.qa_prompt | agent.streaming_llm
            else:
                prompt_input = {
                    "user_input": request.message,
                    "chat_history": chat_history,
                }
                streaming_chain = agent.general_prompt | agent.streaming_llm

            # 流式执行
            full_response = []
            async for chunk in streaming_chain.astream(prompt_input):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response.append(token)
                yield f"event: token\ndata: {json.dumps({'type': 'token', 'content': token})}\n\n"

            # 发送结束信号
            response_text = "".join(full_response)

            # 更新历史
            agent.conversation_history.append({"role": "user", "content": request.message})
            agent.conversation_history.append({"role": "assistant", "content": response_text})

            end_data = {
                'type': 'end',
                'response': response_text,
            }
            yield f"event: end\ndata: {json.dumps(end_data)}\n\n"

        except Exception as e:
            error_msg = str(e)
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ==================== 历史管理 API ====================

@router.post("/history/clear")
async def clear_history(request: ClearHistoryRequest):
    """清除指定会话的对话历史"""
    from agents.news_agent import clear_agent
    clear_agent(request.session_id)

    return {
        "code": 200,
        "message": "历史已清除",
        "data": {"session_id": request.session_id}
    }


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """获取指定会话的对话历史"""
    agent = get_news_agent(session_id)
    history = agent.get_history()

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "session_id": session_id,
            "history": history,
        }
    }
