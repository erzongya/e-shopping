import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

key = "checkpoint:user999:__empty__:1f184f0a-ec4c-69f6-8001-ed12cce84fa3"

# 1. 检查 key 类型
key_type = r.type(key)
print(f"Key 类型: {key_type}")

# 2. 根据类型读取
if key_type == 'ReJSON-RL':
    try:
        data_json = r.execute_command('JSON.GET', key)
        if data_json:
            data = json.loads(data_json)
            print("=== 完整数据 ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 显示对话历史
            chat = data.get('chat', [])
            if chat:
                print(f"\n=== 对话历史 ({len(chat)} 条) ===")
                for i, msg in enumerate(chat):
                    if isinstance(msg, dict):
                        msg_type = msg.get('type', 'unknown')
                        content = msg.get('content', '')
                        print(f"[{i}] {msg_type}: {content}")
                    else:
                        print(f"[{i}] {msg}")

            # 显示 messages（如果有）
            messages = data.get('messages', [])
            if messages:
                print(f"\n=== Messages ({len(messages)} 条) ===")
                for i, msg in enumerate(messages):
                    if isinstance(msg, dict):
                        msg_type = msg.get('type', 'unknown')
                        content = msg.get('content', '')
                        print(f"[{i}] {msg_type}: {content}")
                    else:
                        print(f"[{i}] {msg}")
    except Exception as e:
        print(f"JSON 读取失败: {e}")

elif key_type == 'string':
    value = r.get(key)
    print(f"String 值: {value}")

else:
    print(f"不支持的类型: {key_type}")