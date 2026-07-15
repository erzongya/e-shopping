from abc import ABC, abstractmethod
from pydantic import BaseModel

#所有技能的入参模型都要继承它，做统一规范
class SkillParams(BaseModel):
    """统一技能参数校验模型"""
    pass

class BaseSkill(ABC):
    # 技能元信息，给llm识别
    name:str
    description:str
    params_model:type[SkillParams]

    @abstractmethod
    def run(self,**kwargs):
        """统一执行入口，业务逻辑放这里"""
        pass