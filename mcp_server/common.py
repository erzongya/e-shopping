from mcp.server.fastmcp import FastMCP
from skill.base import BaseSkill
import json
def batch_register_skills(mcp: FastMCP, skill_list: list[type[BaseSkill]], err_log):
    def wrap_factory(skill_ins):
        @mcp.tool(name=skill_ins.name, description=skill_ins.description)
        def wrapper(**kwargs):
            try:
                raw_kwargs = kwargs.get("kwargs", {})
                # 判断如果是字符串就loads解析
                if isinstance(raw_kwargs, str):
                    real_args = json.loads(raw_kwargs)
                else:
                    real_args = raw_kwargs
                args = skill_ins.params_model(** real_args)
                resp_data = skill_ins.run(** args.model_dump())
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