from pydantic import BaseModel

class SkillParams(BaseModel):
    """所有MCP工具参数父类，强制平铺无嵌套"""
    pass

class BaseSkill:
    name: str
    description: str
    params_model: type[SkillParams]

    def run(self, **kwargs):
        raise NotImplementedError("必须实现run业务逻辑")