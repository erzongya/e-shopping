from langgraph.checkpoint.memory import MemorySaver

# 内存会话存储，替代RedisSaver
checkpointer = MemorySaver()

# 置空redis客户端，限流中间件要配套注释
redis_client = None