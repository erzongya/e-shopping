import json
import logging
from mcp.server.fastmcp import FastMCP
from skill.base import BaseSkill

import json
import logging
from mcp.server.fastmcp import FastMCP
from skill.base import BaseSkill
from pydantic import BaseModel

def register_mcp_skill(mcp_server: FastMCP, skill: BaseSkill, log: logging.Logger):
    param_model = skill.params_model

    # 用pydantic模型做入参，让FastMCP自动生成参数schema，LLM才能识别工具
    @mcp_server.tool(
        name=skill.name,
        description=skill.description,
    )
    def run_func(args: param_model):
        try:
            # 平铺参数传给skill.run
            return skill.run(** args.model_dump())
        except Exception as err:
            log.error(f"工具{skill.name}外层异常: {err}", exc_info=True)
            return {"success": False, "msg": f"工具执行异常：{str(err)}", "data": None}

def batch_register_skills(mcp_server: FastMCP, skill_cls_list: list[type[BaseSkill]], log: logging.Logger):
    instances = [cls() for cls in skill_cls_list]
    for ins in instances:
        register_mcp_skill(mcp_server, ins, log)