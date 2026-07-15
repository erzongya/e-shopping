from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from langgraph.checkpoint.redis import RedisSaver
from skill.base import SkillParams, BaseSkill
from config.settings import settings

class CleanExpireCheckpointParams(SkillParams):
    """清理过期会话入参"""
    expire_days: int = 7  # 默认7天前的会话视为过期
    dry_run: bool = False # 仅查询不删除，调试用

class CleanExpireCheckpointSkill(BaseSkill):
    name = "clean_expire_checkpoint"
    description = "清理Redis中过期的LangGraph会话断点缓存，支持定时自动执行、后台接口手动触发"
    params_model = CleanExpireCheckpointParams

    def run(self, **kwargs):
        args = self.params_model(** kwargs)
        expire_sec = args.expire_days * 24 * 60 * 60
        prefix = settings.CHECKPOINT_KEY_PREFIX

        # 初始化Redis Checkpointer
        cp = RedisSaver.from_url(settings.REDIS_URL, prefix=prefix)
        redis_client = cp.redis

        try:
            # 1. 扫描所有checkpoint key
            match_key = f"{prefix}*"
            cursor = 0
            del_count = 0
            scan_count = 0

            while True:
                cursor, keys = redis_client.scan(cursor, match=match_key, count=100)
                if not keys:
                    if cursor == 0:
                        break
                    continue

                for key in keys:
                    scan_count += 1
                    # 获取key剩余存活时间（-1永久，-2不存在）
                    ttl = redis_client.ttl(key)
                    # 无过期时间/已过期则清理
                    if ttl == -1 or ttl <= 0:
                        if not args.dry_run:
                            redis_client.delete(key)
                        del_count += 1
                if cursor == 0:
                    break

            result = {
                "scan_total": scan_count,
                "deleted_count": del_count,
                "expire_days_rule": args.expire_days,
                "dry_run": args.dry_run,
                "msg": f"扫描{scan_count}条会话缓存，清理{del_count}条过期数据"
            }
            return result

        except Exception as e:
            return f"清理过期会话失败：{str(e)}"