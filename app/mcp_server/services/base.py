# mcp_server/services/base.py
"""
MCP 服务基类
"""
from mcp.server.fastmcp import FastMCP
from typing import List, Type, Optional

from app.core.logger import log_info, log_error


class BaseMCPService:
    """MCP 服务基类"""

    def __init__(
            self,
            name: str,
            port: int,
            host: str = "127.0.0.1",
            description: str = "",
            log_level: str = "ERROR"
    ):
        """
        初始化 MCP 服务

        Args:
            name: 服务名称
            port: 服务端口
            host: 服务地址
            description: 服务描述
            log_level: 日志级别
        """
        self.name = name
        self.port = port
        self.host = host
        self.description = description

        # 创建 FastMCP 实例
        self.mcp = FastMCP(
            name=name,
            instructions=description,
            log_level=log_level,
            host=host,
            port=port,
        )

        self._skills_registered = False

    def register_skills(self, skill_cls_list: List[Type]) -> None:
        """
        注册技能

        Args:
            skill_cls_list: 技能类列表
        """
        if self._skills_registered:
            return

        from mcp_server.services.common import batch_register_skills

        batch_register_skills(self.mcp, skill_cls_list, log_error)
        self._skills_registered = True

        log_info("", f"mcp_{self.name}", f"✅ 注册 {len(skill_cls_list)} 个技能")

    def run(self) -> None:
        """启动服务"""
        trace_id = ""
        session_id = f"mcp_{self.name}"

        log_info(trace_id, session_id, f"🚀 {self.name} 服务启动，端口: {self.port}")
        log_info(trace_id, session_id, f"📦 服务描述: {self.description}")

        try:
            self.mcp.run(transport="streamable-http")
        except Exception as e:
            log_error(trace_id, session_id, f"❌ {self.name} 服务启动失败", e)
            raise

    def get_mcp(self) -> FastMCP:
        """获取 FastMCP 实例"""
        return self.mcp