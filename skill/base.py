from pydantic import BaseModel
class SkillParams(BaseModel):
    pass

class BaseSkill:
    name: str
    description: str
    params_model: type[SkillParams]
    def run(self,** kwargs):
        args = self.params_model(**kwargs)
        return self._execute(args)
    def _execute(self, args):
        raise NotImplementedError