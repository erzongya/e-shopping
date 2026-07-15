from langgraph.checkpoint.memory import MemorySaver


checkpointer = MemorySaver()



# import redis
# from langgraph.checkpoint.redis import RedisSaver
# from config.settings import settings
#
# # 1. 拼接Redis连接URL（RedisSaver必须传url字符串）
# if getattr(settings, "REDIS_PASSWORD", None):
#     redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
# else:
#     redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
#
# # 2. 业务全局Redis客户端（自己业务代码用）
# redis_client = redis.Redis.from_url(
#     redis_url,
#     decode_responses=True,
#     socket_timeout=5,
#     retry_on_timeout=True
# )
#
# # 3. 实例化LangGraph持久化，只传url字符串，不要传redis_client对象
# checkpointer = RedisSaver(redis_url)