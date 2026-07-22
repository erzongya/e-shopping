from mcp_server.client.manager import mcp_manager
from retrieval.reteriever import Retriever

def build_system_prompt(user_query: str) -> str:
    """动态生成System Prompt,从MCPManager获取所有工具信息，拼成文字
    """
    # 1. 获取所有工具元数据
    tools_meta = mcp_manager.get_tools_meta()

    # 🆕 RAG 检索
    rag_context = ""
    if Retriever.is_relevant(user_query):
        _, context = Retriever.search(user_query, top_k=3)
        if context:
            rag_context = f"""
                            # 📚 知识库参考（请基于以下官方政策回答）
                            {context}
                            """
        else:
            rag_context = "\n# 📚 知识库暂无相关信息\n"


    # 2. 把工具信息拼成文字
    tool_text = ""
    for tool_name, tool_info in tools_meta.items():
        tool_text += f"• {tool_name}\n"
        tool_text += f"  描述: {tool_info['description']}\n"

        # 拼参数
        schema = tool_info.get('schema', {})
        props = schema.get('properties', {})
        required = schema.get('required', [])

        if props:
            param_text = ""
            for param_name, param_info in props.items():
                is_required = "（必填）" if param_name in required else ""
                param_type = param_info.get('type', 'string')
                param_text += f"    - {param_name}{is_required}: {param_type}\n"
            tool_text += f"  参数:\n{param_text}"
        else:
            tool_text += "  参数: 无\n"

        tool_text += "\n"

    # 3. 如果没有任何工具，给个提示
    if not tools_meta:
        tool_text = "（当前没有可用的工具）\n"

    # 4. 组装完整的System Prompt（分层结构）
    system_prompt = f"""
# 角色
你是专业电商智能助手，帮助用户处理商品查询、订单查询、售后咨询等问题。

# 强制规则
1. 每次最多调用5个工具
2. 必须按工具的参数格式传参，不要编造参数
3. 涉及退款、取消订单等操作，必须让用户二次确认
{rag_context}

# 可用工具列表
{tool_text}

# 输出格式
- 如果需要调用工具，输出JSON数组：[{{"tool": "工具名", "args": {{...}}}}]
- 如果不需要调用工具，直接输出自然语言回答

# 异常处理（从工具返回结果中判断）
1. 工具返回 "0条" 或 "无数据" → 告知用户 "未查询到相关信息，请确认条件后重试"
2. 工具返回包含 "错误" 或 "失败" → 告知用户 "系统繁忙，请稍后重试"
3. 工具返回正常数据 → 整理成友好回答

# 用户当前问题
{user_query}

请根据以上信息，处理用户的问题。
"""
    return system_prompt


def get_functions_for_llm():
    """
    获取OpenAI Function Calling格式的工具列表
    用于 llm.bind_tools()
    """
    tools_meta = mcp_manager.get_tools_meta()

    functions = []
    for tool_name, tool_info in tools_meta.items():
        functions.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_info['description'],
                "parameters": tool_info['schema']
            }
        })

    return functions

