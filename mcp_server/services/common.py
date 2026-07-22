from mcp.server.fastmcp import FastMCP
from mcp_server.skill.base import BaseSkill


def batch_register_skills(mcp: FastMCP, skill_list: list[type[BaseSkill]], err_log):
    """批量注册 Skill 到 MCP 服务"""

    def wrap_factory(skill_ins):
        @mcp.tool(name=skill_ins.name, description=skill_ins.description)
        def wrapper(params: dict):
            try:
                args = skill_ins.params_model(**params)
                resp_data = skill_ins.run(**args.model_dump())
                return {
                    "content": [{"type": "text", "text": resp_data}],
                    "isError": False
                }
            except Exception as e:
                err_log(trace_id="", session_id="system_mcp_user", msg=f"工具{skill_ins.name}执行异常:{str(e)}")
                return {
                    "content": [{"type": "text", "text": f"工具执行失败:{str(e)}"}],
                    "isError": True
                }

        return wrapper

    for skill_cls in skill_list:
        ins = skill_cls()
        wrap_factory(ins)