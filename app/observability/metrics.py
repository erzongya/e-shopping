# observability/metrics.py
"""
指标收集器 - 程序运行的"记账本"

作用：
1. 记录所有 LLM 调用
2. 记录所有工具调用
3. 汇总每次对话的统计
4. 持久化到文件

特点：
- 单例模式：整个程序只有一个实例，所有地方共用
- 线程安全：多个用户同时访问不会乱
"""

import time
import json
import os
from threading import Lock
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from app.observability.models import (
    LLMCallRecord,
    ToolCallRecord,
    ConversationSummary
)


class MetricsCollector:
    """
    指标收集器
    
    使用方式：
        metrics = MetricsCollector()  # 获取全局单例
        
        # 对话开始
        metrics.start_conversation("session_001", "user_123")
        
        # 记录 LLM 调用
        metrics.record_llm_call("gpt-4", 100, 50, 500, True, 1)
        
        # 记录工具调用
        metrics.record_tool_call("query_order", True, 200)
        
        # 对话结束
        summary = metrics.end_conversation()
    """

    # ============================================================
    # 单例模式：保证整个程序只有一个实例
    # ============================================================
    # 为什么需要单例？
    # 如果有多个实例，每个实例都有自己的数据，
    # 那 A 用户的数据可能在实例1，B 用户的数据在实例2，
    # 查询统计时就乱了。
    # 
    # 单例保证所有地方用的是同一个"账本"。
    # ============================================================

    _instance = None          # 唯一实例
    _lock = Lock()            # 线程锁，防止多人同时翻账本

    def __new__(cls):
        """
        __new__ 控制实例创建
        第一次调用：创建实例
        后续调用：返回已有实例
        """
        if cls._instance is None:
            with cls._lock:   # 拿锁，防止多线程同时创建
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        __init__ 初始化实例
        只会执行一次（因为 _initialized 标志）
        """
        if self._initialized:
            return
        self._initialized = True

        # -------- 当前对话数据（临时） --------
        # 正在进行的对话，数据从这里记录
        self._current_llm_calls: List[LLMCallRecord] = []      # 本次对话的 LLM 调用列表
        self._current_tool_calls: List[ToolCallRecord] = []    # 本次对话的工具调用列表
        self._conversation_start: Optional[float] = None       # 开始时间（时间戳）
        self._session_id: str = ""                             # 会话 ID
        self._user_id: str = ""                                # 用户 ID

        # -------- 历史数据（永久） --------
        # 所有历史对话的数据，用于统计
        self._history_llm_calls: List[LLMCallRecord] = []          # 所有 LLM 调用历史
        self._history_tool_calls: List[ToolCallRecord] = []        # 所有工具调用历史
        self._history_conversations: List[ConversationSummary] = []  # 所有对话历史

        # 启动时加载之前保存的数据
        self._load_from_file()

        self._lock = Lock()

    # ============================================================
    # 对话生命周期管理
    # ============================================================

    def start_conversation(self, session_id: str, user_id: str = "anonymous"):
        """
        开始一次对话
        
        什么时候调用：用户发消息时
        做什么：
            1. 清空临时数据
            2. 记录开始时间
            3. 保存会话信息
        
        参数：
            session_id: 会话 ID，用于关联同一次对话的多轮消息
            user_id: 用户 ID，用于分析用户行为
        """
        with self._lock:  # 拿锁，防止多线程同时修改
            # 清空上次对话的临时数据
            self._current_llm_calls = []
            self._current_tool_calls = []
            # 记录开始时间
            self._conversation_start = time.time()
            # 保存会话信息
            self._session_id = session_id
            self._user_id = user_id

    def end_conversation(self, status: str = "success", error_info: str = None):
        """
        结束一次对话
        
        什么时候调用：对话结束时（成功或失败）
        做什么：
            1. 计算总耗时
            2. 汇总所有数据
            3. 保存到历史
            4. 持久化到文件
            5. 清空临时数据
        
        参数：
            status: "success" 或 "error" 或 "timeout"
            error_info: 如果失败，记录错误信息
        """
        with self._lock:
            # 如果没有开始对话，什么都不做
            if self._conversation_start is None:
                return

            # -------- 1. 计算总耗时 --------
            end_time = time.time()
            total_ms = (end_time - self._conversation_start) * 1000

            # -------- 2. 汇总 Token 消耗 --------
            total_input = sum(c.input_tokens for c in self._current_llm_calls)
            total_output = sum(c.output_tokens for c in self._current_llm_calls)
            total_tokens = total_input + total_output

            # -------- 3. 汇总调用次数 --------
            llm_count = len(self._current_llm_calls)
            tool_count = len(self._current_tool_calls)
            tool_success = sum(1 for t in self._current_tool_calls if t.success)
            tool_fail = tool_count - tool_success

            # -------- 4. 生成对话汇总 --------
            summary = ConversationSummary(
                session_id=self._session_id,
                user_id=self._user_id,
                start_time=datetime.fromtimestamp(self._conversation_start).isoformat(),
                end_time=datetime.fromtimestamp(end_time).isoformat(),
                total_duration_ms=total_ms,
                llm_call_count=llm_count,
                tool_call_count=tool_count,
                tool_success_count=tool_success,
                tool_fail_count=tool_fail,
                total_input_tokens=total_input,
                total_output_tokens=total_output,
                total_tokens=total_tokens,
                status=status,
                error_info=error_info
            )

            # -------- 5. 存入历史 --------
            self._history_conversations.append(summary)
            self._history_llm_calls.extend(self._current_llm_calls)
            self._history_tool_calls.extend(self._current_tool_calls)

            # -------- 6. 持久化到文件 --------
            self._save_to_file()

            # -------- 7. 清空临时数据 --------
            self._current_llm_calls = []
            self._current_tool_calls = []
            self._conversation_start = None

            return summary


    # 记录具体事件
    def record_llm_call(self,model: str,input_tokens: int,output_tokens: int,duration_ms: float,has_tool_calls: bool,tool_call_count: int = 0):
        """
        记录一次 LLM 调用
        
        什么时候调用：每次调用 LLM 后
        记什么：用了什么模型、花了多少 token、用了多久
        
        这些数据用于：
            - 成本分析：每天花了多少 API 费用
            - 性能分析：哪个模型响应最快
            - 行为分析：LLM 调工具的频率
        """
        with self._lock:
            record = LLMCallRecord(
                timestamp=datetime.now().isoformat(),
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                duration_ms=duration_ms,
                has_tool_calls=has_tool_calls,
                tool_call_count=tool_call_count
            )
            self._current_llm_calls.append(record)

    def record_tool_call(self,tool_name: str,success: bool,duration_ms: float,error_type: str = None):
        """
        记录一次工具调用
        
        什么时候调用：每次调用 MCP 工具后
        记什么：调了什么工具、成功还是失败、用了多久
        
        这些数据用于：
            - 稳定性分析：哪个工具最容易失败
            - 性能分析：哪个工具最慢
            - 错误分析：主要是什么类型的错误
        """
        with self._lock:
            record = ToolCallRecord(
                timestamp=datetime.now().isoformat(),
                tool_name=tool_name,
                success=success,
                duration_ms=duration_ms,
                error_type=error_type
            )
            self._current_tool_calls.append(record)


    # 查询统计
    def get_current_stats(self) -> Dict[str, Any]:
        """
        获取当前对话的实时统计
        
        用于：对话进行中查看进度
        
        返回：
            {
                "session_id": "session_001",
                "llm_calls": 3,          # 已调 LLM 次数
                "tool_calls": 2,          # 已调工具次数
                "tool_success": 2,        # 工具成功数
                "tool_fail": 0,           # 工具失败数
                "input_tokens": 500,      # 已用输入 token
                "output_tokens": 150,     # 已用输出 token
                "total_tokens": 650,      # 总 token
                "duration_ms": 3200       # 已用时间
            }
        """
        with self._lock:
            # 如果没有开始对话，返回空
            if self._conversation_start is None:
                return {}

            total_input = sum(c.input_tokens for c in self._current_llm_calls)
            total_output = sum(c.output_tokens for c in self._current_llm_calls)
            total_tokens = total_input + total_output

            tool_success = sum(1 for t in self._current_tool_calls if t.success)
            tool_fail = len(self._current_tool_calls) - tool_success

            return {
                "session_id": self._session_id,
                "user_id": self._user_id,
                "llm_calls": len(self._current_llm_calls),
                "tool_calls": len(self._current_tool_calls),
                "tool_success": tool_success,
                "tool_fail": tool_fail,
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_tokens,
                "duration_ms": (time.time() - self._conversation_start) * 1000,
            }

    def get_global_stats(self) -> Dict[str, Any]:
        """
        获取全局统计数据
        
        用于：查看整体运行情况
        
        返回：
            {
                "total_conversations": 100,      # 总对话数
                "total_llm_calls": 500,           # 总 LLM 调用
                "total_tool_calls": 300,          # 总工具调用
                "tool_success_rate": 95.5,        # 工具成功率 %
                "total_tokens": 250000,           # 总 token
                "error_distribution": {           # 错误分布
                    "empty_result": 5,
                    "execution_error": 2
                },
                "avg_tokens_per_conv": 2500       # 平均每次对话 token
            }
        """
        with self._lock:
            total_conversations = len(self._history_conversations)
            total_llm_calls = len(self._history_llm_calls)
            total_tool_calls = len(self._history_tool_calls)

            # 工具成功率
            tool_success = sum(1 for t in self._history_tool_calls if t.success)
            tool_success_rate = tool_success / total_tool_calls if total_tool_calls > 0 else 0

            # Token 统计
            total_input = sum(c.input_tokens for c in self._history_llm_calls)
            total_output = sum(c.output_tokens for c in self._history_llm_calls)
            total_tokens = total_input + total_output

            # 错误类型分布
            error_counts = defaultdict(int)
            for t in self._history_tool_calls:
                if not t.success and t.error_type:
                    error_counts[t.error_type] += 1

            return {
                "total_conversations": total_conversations,
                "total_llm_calls": total_llm_calls,
                "total_tool_calls": total_tool_calls,
                "tool_success_rate": round(tool_success_rate * 100, 2),
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_tokens": total_tokens,
                "error_distribution": dict(error_counts),
                "avg_tokens_per_conversation": total_tokens // total_conversations if total_conversations > 0 else 0,
            }

    def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        """
        获取最近的对话记录
        
        用于：查看最近的对话详情
        
        参数：
            limit: 返回多少条，默认 20
        """
        with self._lock:
            recent = self._history_conversations[-limit:]
            return [self._to_dict(s) for s in recent]

    def _to_dict(self, obj) -> Dict:
        """把 dataclass 转成字典"""
        if hasattr(obj, "__dataclass_fields__"):
            return {k: self._to_dict(v) for k, v in obj.__dict__.items()}
        if isinstance(obj, list):
            return [self._to_dict(i) for i in obj]
        return obj


    # 持久化（保存到文件）
    def _save_to_file(self):
        """
        保存到 JSON 文件
        
        为什么需要持久化？
        - 服务重启后数据不丢失
        - 可以分析历史趋势
        
        保存位置：observability/metrics_data.json
        """
        try:
            # 确保目录存在
            os.makedirs("observability", exist_ok=True)

            data = {
                "conversations": [self._to_dict(c) for c in self._history_conversations],
                "llm_calls": [self._to_dict(c) for c in self._history_llm_calls],
                "tool_calls": [self._to_dict(c) for c in self._history_tool_calls],
                "updated_at": datetime.now().isoformat()
            }

            with open("observability/metrics_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[Metrics] 保存失败: {e}")

    def _load_from_file(self):
        """
        从文件加载历史数据
        
        什么时候调用：服务启动时
        做什么：恢复之前保存的数据
        """
        try:
            filepath = "observability/metrics_data.json"
            if not os.path.exists(filepath):
                return

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 恢复对话记录
            for c in data.get("conversations", []):
                self._history_conversations.append(ConversationSummary(**c))

            # 恢复 LLM 调用记录
            for c in data.get("llm_calls", []):
                self._history_llm_calls.append(LLMCallRecord(**c))

            # 恢复工具调用记录
            for c in data.get("tool_calls", []):
                self._history_tool_calls.append(ToolCallRecord(**c))

            print(f"[Metrics] 加载历史: {len(self._history_conversations)} 条对话")

        except Exception as e:
            print(f"[Metrics] 加载失败: {e}")


# 全局单例
metrics = MetricsCollector()