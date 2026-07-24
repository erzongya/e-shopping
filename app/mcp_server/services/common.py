from mcp.server.fastmcp import FastMCP
from app.mcp_server.skills.base import BaseSkill
from app.core.logger import log_error
import json
from functools import partial


def batch_register_skills(mcp: FastMCP, skill_list: list[type[BaseSkill]], err_log):
    for skill_cls in skill_list:
        ins = skill_cls()
        params_model = ins.params_model

        async def execute(skill_ins, model, **kwargs) -> dict:
            try:
                if "kwargs" in kwargs:
                    if isinstance(kwargs["kwargs"], str):
                        real_args = json.loads(kwargs["kwargs"])
                    else:
                        real_args = kwargs["kwargs"]
                else:
                    real_args = kwargs

                params = model(**real_args)
                resp_data = await skill_ins.run(**params.model_dump())

                # ✅ 如果 resp_data 有 code 和 data，只取 data
                if isinstance(resp_data, dict) and "code" in resp_data and resp_data.get("code") == 0:
                    result_data = resp_data.get("data", resp_data)
                else:
                    result_data = resp_data

                return {
                    "content": [{"type": "text", "text": json.dumps(result_data, ensure_ascii=False)}],
                    "isError": False
                }
            except Exception as e:
                err_log(trace_id="", session_id="system_mcp_user", msg=f"工具{skill_ins.name}执行异常:{str(e)}")
                return {
                    "content": [{"type": "text", "text": json.dumps({"error": str(e)}, ensure_ascii=False)}],
                    "isError": True
                }

        wrapped = partial(execute, ins, params_model)
        wrapped.__name__ = ins.name
        wrapped.__doc__ = ins.description

        mcp.tool(name=ins.name, description=ins.description)(wrapped)