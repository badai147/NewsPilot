import json

import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=REDIS_DB,
    decode_responses=True
)

async def get_cache(key: str):
    """
    读取字符串
    """
    
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None

async def get_json_cache(key: str):
    """
    读取列表或字典
    """
    
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data) # 序列化
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败：{e}")
        return None
    
async def set_cache(key: str, value: str, expire: int = 3600):
    """
    设置缓存
    """
    try:
        if isinstance(value, (dict, list)):
            # 转字符串再存
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, value, ex=expire)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False
    
    