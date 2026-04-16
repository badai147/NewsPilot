"""
新闻总结与聊天 Agent
基于 LangChain 0.1.x+ 最新版本，支持 OpenAI 兼容接口
"""

import os
import re
from typing import List, Dict, Any, Optional, Callable, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import ChatGeneration, LLMResult

import asyncio

from dotenv import load_dotenv

load_dotenv()

# ==================== 配置类 ====================

class AgentConfig:
    """Agent 配置"""
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.temperature = 0.7
        self.max_tokens = 2000
        
        print(self.openai_api_key, self.openai_base_url, self.model_name)


# ==================== 流式回调处理器 ====================

class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器 - LangChain 最新版 API"""

    def __init__(self, chunk_handler: Optional[Callable] = None):
        self.chunk_handler = chunk_handler
        self.tokens: List[str] = []
        self.generation_metadata: Dict[str, Any] = {}

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """LLM 输出新 token 时调用"""
        self.tokens.append(token)
        if self.chunk_handler:
            self.chunk_handler(token)

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """LLM 生成结束时调用"""
        if response.generations:
            gen = response.generations[0][0]
            if isinstance(gen, ChatGeneration):
                self.generation_metadata = {
                    "finish_reason": gen.generation_info.get("finish_reason") if gen.generation_info else None,
                }


# ==================== 异步生成器支持 ====================

class AsyncIteratorCallbackHandler(BaseCallbackHandler):
    """异步迭代器回调处理器 - 用于 SSE 流式输出"""

    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.done = False

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """将 token 放入队列"""
        if not self.done:
            await self.queue.put(token)

    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """标记完成"""
        self.done = True
        await self.queue.put(None)  # None 表示结束

    def __aiter__(self) -> "AsyncIteratorCallbackHandler":
        return self

    async def __anext__(self) -> str:
        token = await self.queue.get()
        if token is None:
            raise StopAsyncIteration
        return token


# ==================== 新闻总结 Agent ====================

class NewsSummaryAgent:
    """
    新闻总结与聊天 Agent - LangChain 0.2.x 兼容版本

    功能：
    1. 自动总结新闻内容，提取关键信息
    2. 支持针对新闻内容的多轮对话
    3. 完整的流式输出支持
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self._setup_llm()
        self._setup_chains()
        self.conversation_history: List[Dict[str, str]] = []

    def _setup_llm(self):
        """初始化 LLM - 使用新版 ChatOpenAI"""
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_base_url,
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            streaming=False,  # 非流式，用于普通调用
        )

        # 流式 LLM 实例
        self.streaming_llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_base_url,
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            streaming=True,  # 启用流式
        )

    def _setup_chains(self):
        """初始化 Chains - LangChain 0.1.x+ 新版 API"""

        # ========== 新闻总结 Chain ==========
        summary_system_prompt = """你是一个专业的新闻分析师，负责对新闻内容进行深度分析和总结。

请从以下几个方面对新闻进行分析：
1. **核心事件**：新闻的主要事件或主题是什么？
2. **关键人物**：涉及哪些重要人物或机构？
3. **重要细节**：时间、地点、数据等关键信息
4. **背景分析**：事件的背景或原因
5. **影响评估**：该事件可能产生的影响或意义

请用简洁、有条理的方式输出分析结果，使用 Markdown 格式美化输出。"""

        # 新版 ChatPromptTemplate 使用
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", summary_system_prompt),
            ("human", "请分析以下新闻内容：\n\n{news_content}"),
        ])

        # 新版 chain 使用方式
        self.summary_chain = self.summary_prompt | self.llm

        # ========== 问答 Chain ==========
        qa_system_prompt = """你是一个热情的新闻助手，基于提供的新闻内容回答用户的问题。

Guidelines:
1. 基于新闻内容和总结回答问题
2. 如果新闻内容中没有相关信息，请明确告知用户
3. 回答要准确、简洁、有礼貌
4. 可以适当补充与新闻相关的背景知识
5. 使用 Markdown 格式美化输出"""

        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{user_input}"),
        ])

        self.qa_chain = self.qa_prompt | self.llm

        # ========== 通用对话 Chain ==========
        general_system_prompt = """你是一个友好、智能的新闻资讯助手。

你可以：
1. 回答用户关于新闻的各类问题
2. 讨论当前热点话题
3. 提供信息查询和建议
4. 进行友好的闲聊

请保持回答简洁、有帮助，使用 Markdown 格式美化输出。"""

        self.general_prompt = ChatPromptTemplate.from_messages([
            ("system", general_system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{user_input}"),
        ])

        self.general_chain = self.general_prompt | self.llm

    def _build_chat_history(self) -> List[Any]:
        """构建聊天历史（LangChain 消息格式）"""
        chat_history = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))
        return chat_history

    async def summarize_news(
        self,
        news_content: str,
        news_title: str = "",
        news_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        总结新闻内容（非流式）

        Args:
            news_content: 新闻正文内容
            news_title: 新闻标题
            news_id: 新闻ID（可选）

        Returns:
            包含总结结果的字典
        """
        max_content_length = 8000
        if len(news_content) > max_content_length:
            news_content = news_content[:max_content_length] + "..."

        try:
            input_data = {
                "news_content": f"标题：{news_title}\n\n内容：{news_content}" if news_title else news_content
            }

            # 新版 LangChain invoke 方式
            response = await self.summary_chain.ainvoke(input_data)
            summary_text = response.content if hasattr(response, 'content') else str(response)

            # 保存到历史
            self.conversation_history = [
                {"role": "system", "content": f"新闻标题：{news_title}" if news_title else ""},
                {"role": "assistant", "content": summary_text},
            ]

            return {
                "success": True,
                "news_id": news_id,
                "title": news_title,
                "summary": summary_text,
                "key_points": self._extract_key_points(summary_text),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "news_id": news_id,
            }

    async def summarize_news_stream(
        self,
        news_content: str,
        news_title: str = "",
        news_id: Optional[int] = None,
        chunk_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        流式总结新闻内容 - LangChain 最新流式 API

        Args:
            news_content: 新闻正文内容
            news_title: 新闻标题
            news_id: 新闻ID
            chunk_callback: 流式回调函数

        Returns:
            完整结果
        """
        max_content_length = 8000
        if len(news_content) > max_content_length:
            news_content = news_content[:max_content_length] + "..."

        try:
            input_data = {
                "news_content": f"标题：{news_title}\n\n内容：{news_content}" if news_title else news_content
            }

            # 使用流式 LLM
            streaming_chain = self.summary_prompt | self.streaming_llm

            # 收集所有 token
            full_text = []

            async for chunk in streaming_chain.astream(input_data):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_text.append(token)
                if chunk_callback:
                    chunk_callback(token)

            summary_text = "".join(full_text)

            self.conversation_history = [
                {"role": "system", "content": f"新闻标题：{news_title}" if news_title else ""},
                {"role": "assistant", "content": summary_text},
            ]

            return {
                "success": True,
                "news_id": news_id,
                "title": news_title,
                "summary": summary_text,
                "key_points": self._extract_key_points(summary_text),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "news_id": news_id,
            }

    async def chat(
        self,
        user_input: str,
        news_summary: Optional[str] = None,
        news_content: Optional[str] = None,
        news_title: str = "",
    ) -> Dict[str, Any]:
        """
        聊天对话（单轮，非流式）

        Args:
            user_input: 用户输入
            news_summary: 新闻总结（可选）
            news_content: 新闻内容（可选）
            news_title: 新闻标题

        Returns:
            AI 回复
        """
        try:
            chat_history = self._build_chat_history()

            if news_summary or news_content:
                context_prompt = ""
                if news_summary:
                    context_prompt += f"以下是新闻【{news_title}】的总结：\n{news_summary}\n\n"
                if news_content:
                    truncated_content = news_content[:3000] + "..." if len(news_content) > 3000 else news_content
                    context_prompt += f"新闻原文：\n{truncated_content}\n\n"

                enhanced_input = context_prompt + f"用户问题：{user_input}"

                response = await self.qa_chain.ainvoke({
                    "user_input": enhanced_input,
                    "chat_history": chat_history,
                })
            else:
                response = await self.general_chain.ainvoke({
                    "user_input": user_input,
                    "chat_history": chat_history,
                })

            ai_response = response.content if hasattr(response, 'content') else str(response)

            # 更新历史
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            return {
                "success": True,
                "response": ai_response,
                "chat_history": self.conversation_history[-10:],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def chat_stream(
        self,
        user_input: str,
        news_summary: Optional[str] = None,
        news_content: Optional[str] = None,
        news_title: str = "",
        chunk_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        流式聊天对话 - LangChain 最新流式 API

        Args:
            user_input: 用户输入
            news_summary: 新闻总结
            news_content: 新闻内容
            news_title: 新闻标题
            chunk_callback: 流式回调函数

        Returns:
            完整回复
        """
        try:
            chat_history = self._build_chat_history()

            # 构建输入
            if news_summary:
                prompt_input = {
                    "user_input": f"参考以下新闻内容回答：\n\n{news_summary}\n\n用户问题：{user_input}",
                    "chat_history": chat_history,
                }
                streaming_chain = self.qa_prompt | self.streaming_llm
            else:
                prompt_input = {
                    "user_input": user_input,
                    "chat_history": chat_history,
                }
                streaming_chain = self.general_prompt | self.streaming_llm

            # 流式执行
            full_text = []
            async for chunk in streaming_chain.astream(prompt_input):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_text.append(token)
                if chunk_callback:
                    chunk_callback(token)

            ai_response = "".join(full_text)

            # 更新历史
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            return {
                "success": True,
                "response": ai_response,
                "chat_history": self.conversation_history[-10:],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def chat_stream_generator(
        self,
        user_input: str,
        news_summary: Optional[str] = None,
        news_content: Optional[str] = None,
        news_title: str = "",
    ) -> AsyncIterator[str]:
        """
        流式聊天对话 - 生成器版本（用于 SSE）

        Yields:
            每个 token
        """
        try:
            chat_history = self._build_chat_history()

            if news_summary:
                prompt_input = {
                    "user_input": f"参考以下新闻内容回答：\n\n{news_summary}\n\n用户问题：{user_input}",
                    "chat_history": chat_history,
                }
                streaming_chain = self.qa_prompt | self.streaming_llm
            else:
                prompt_input = {
                    "user_input": user_input,
                    "chat_history": chat_history,
                }
                streaming_chain = self.general_prompt | self.streaming_llm

            full_text = []
            async for chunk in streaming_chain.astream(prompt_input):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_text.append(token)
                yield token

            ai_response = "".join(full_text)
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

        except Exception as e:
            yield f"[ERROR] {str(e)}"

    def _extract_key_points(self, summary_text: str) -> List[str]:
        """从总结中提取关键点"""
        key_points = []
        lines = summary_text.split("\n")

        for line in lines:
            line = line.strip()
            # 移除 Markdown 标记
            if line.startswith("#") or line.startswith("**"):
                line = re.sub(r'^#+\s*', '', line)
                line = re.sub(r'^\*\*|\*\*$', '', line)

            if line and len(line) > 10 and len(line) < 200:
                key_points.append(line)

        return key_points[:5]

    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history


# ==================== Agent 工厂 ====================

_agent_instances: Dict[str, NewsSummaryAgent] = {}


def get_news_agent(session_id: str = "default") -> NewsSummaryAgent:
    """获取或创建 NewsAgent 实例"""
    if session_id not in _agent_instances:
        _agent_instances[session_id] = NewsSummaryAgent()
    return _agent_instances[session_id]


def clear_agent(session_id: str):
    """清除指定会话的 Agent"""
    if session_id in _agent_instances:
        _agent_instances[session_id].clear_history()
