# observability/models.py
"""
数据模型：定义要记录的数据结构
就像记账本里每一页的格式
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMCallRecord:
    """
    一次 LLM 调用的记录

    什么时候记录：每次调用 ChatGPT/DeepSeek 等模型后
    用来分析：token 消耗、调用频率、响应速度
    """
    timestamp: str  # 调用时间，如 "2026-07-22 12:30:00"
    model: str  # 模型名称，如 "gpt-4" 或 "deepseek-chat"
    input_tokens: int  # 输入用了多少 token（你的问题）
    output_tokens: int  # 输出用了多少 token（模型的回答）
    total_tokens: int  # 总共用了多少 token = input + output
    duration_ms: float  # 调用花了多少毫秒
    has_tool_calls: bool  # 这次调用有没有要求调用工具
    tool_call_count: int = 0  # 如果调用了工具，调了几个


@dataclass
class ToolCallRecord:
    """
    一次工具调用的记录

    什么时候记录：每次调用 MCP 工具后
    用来分析：哪个工具最常用、哪个工具容易失败
    """
    timestamp: str  # 调用时间
    tool_name: str  # 工具名称，如 "query_user_order"
    success: bool  # 是否执行成功
    duration_ms: float  # 执行耗时（毫秒）
    error_type: Optional[str] = None  # 如果失败，是什么类型：
    # "empty_result"   - 返回空数据
    # "validation_error" - 参数错误
    # "execution_error"  - 执行异常
    # "timeout"          - 超时


@dataclass
class ConversationSummary:
    """
    一次完整对话的汇总

    什么时候记录：每次用户对话结束后
    用来分析：整体表现、成本估算、用户体验
    """
    session_id: str  # 会话 ID，标识一次对话
    user_id: str  # 用户 ID
    start_time: str  # 开始时间
    end_time: str  # 结束时间
    total_duration_ms: float  # 总耗时（毫秒）

    # 调用次数
    llm_call_count: int  # 调了几次 LLM
    tool_call_count: int  # 调了几次工具
    tool_success_count: int  # 工具成功几次
    tool_fail_count: int  # 工具失败几次

    # Token 消耗
    total_input_tokens: int  # 总输入 token
    total_output_tokens: int  # 总输出 token
    total_tokens: int  # 总 token = input + output

    # 结果
    status: str  # "success" 成功 / "error" 失败 / "timeout" 超时
    error_info: Optional[str] = None  # 如果失败，错误信息