"""
MCP 技能基类
"""
from typing import Dict, Any, Type
from pydantic import BaseModel


class SkillParams(BaseModel):
    """技能参数基类"""
    pass


class BaseSkill:
    """技能基类"""

    name: str = ""
    description: str = ""
    params_model: Type[SkillParams] = SkillParams

    def __init__(self):
        self.context: Dict[str, Any] = {}

    async def run(self, **kwargs) -> Dict[str, Any]:
        """异步执行技能"""
        return await self._run_async(**kwargs)

    async def _run_async(self, **kwargs) -> Dict[str, Any]:
        """子类实现具体的异步逻辑"""
        raise NotImplementedError