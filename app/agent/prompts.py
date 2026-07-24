# agent/prompts.py
"""
System Prompt 构建器
"""
from app.mcp_server.manager import mcp_manager
from app.retrieval.reteriever import Retriever  # 修正拼写


def build_system_prompt(user_query: str, history: list = None) -> str:
    """
    动态构建 System Prompt

    Args:
        user_query: 当前用户问题
        history: 历史对话列表 [{"role": "user", "content": "..."}, ...]

    Returns:
        完整的 System Prompt
    """
    # 1. 获取工具列表
    tools_text = _get_tools_text()

    # 2. RAG 检索
    rag_text = _get_rag_context(user_query)

    # 3. 历史对话
    history_text = _get_history_text(history, user_query)

    # 4. 组装 Prompt
    return f"""
# 角色
你是专业电商智能助手，帮助用户处理商品查询、订单查询、售后咨询等问题。

# 规则
1. 需要查询数据时，必须调用对应的工具
2. 按工具参数格式传参，不要编造参数
3. 涉及退款、取消订单等操作，必须让用户二次确认

# 知识库参考
{rag_text}

# 可用工具
{tools_text}

# 历史信息
{history_text}

# 当前问题
用户: {user_query}

请处理用户的问题。
"""


def _get_tools_text() -> str:
    """获取工具描述文本"""
    try:
        tools_meta = mcp_manager.get_tools_meta()
    except Exception:
        return "暂无可用工具\n"

    if not tools_meta:
        return "暂无可用工具\n"

    lines = []
    for name, info in tools_meta.items():
        lines.append(f"工具名称: {name}")
        lines.append(f"描述: {info.get('description', '无描述')}")

        schema = info.get("schema", {})
        properties = schema.get("properties", {})

        if properties:
            lines.append("参数:")
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "any")
                param_desc = param_info.get("description", "")
                lines.append(f"  - {param_name}: {param_type} ({param_desc})")
        else:
            lines.append("参数: 无")
        lines.append("")

    return "\n".join(lines)

def _get_rag_context(user_query: str) -> str:
    """RAG 检索"""
    try:
        if Retriever.is_relevant(user_query):
            _, context = Retriever.search(user_query, top_k=3)
            if context:
                return f"\n# 知识库参考\n{context}\n"
    except Exception:
        pass
    return ""


def _get_history_text(history: list, user_query: str) -> str:
    """格式化历史对话"""
    if not history:
        return ""

    lines = ["\n# 对话历史"]
    for msg in history[-6:]:  # 最近6条
        role = "用户" if msg["role"] == "user" else "助手"
        lines.append(f"{role}: {msg['content']}")
    lines.append(f"\n用户当前问题: {user_query}")

    return "\n".join(lines)


def get_functions_for_llm():
    """获取 OpenAI Function Calling 格式的工具列表"""
    try:
        tools_meta = mcp_manager.get_tools_meta()
    except Exception:
        return []

    functions = []
    for name, info in tools_meta.items():
        functions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info.get('description', f'{name}工具'),
                "parameters": info.get('schema', {"type": "object", "properties": {}})
            }
        })
    return functions


# ==================== 兼容旧代码 ====================

def build_tool_call_prompt(tool_name: str, tool_args: dict) -> str:
    return f"正在调用工具 {tool_name}，参数: {tool_args}"


def build_error_prompt(error: str) -> str:
    return f"抱歉，处理您的请求时遇到问题：{error}。请稍后重试。"