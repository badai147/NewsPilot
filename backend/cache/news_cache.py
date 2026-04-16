from typing import List, Dict, Any, Optional

from config.cache_conf import get_json_cache, set_cache

CATEFORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news:list:"

async def get_cached_categories():
    """
    获取新闻分类缓存
    """
    
    return await get_json_cache(CATEFORIES_KEY)

async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    """
    写入新闻分类缓存：缓存数据和时间
    """
    
    return await set_cache(CATEFORIES_KEY, data, expire)

async def set_cache_news_list(
    category_id: Optional[int],
    page: int,
    size: int,
    news_list: List[Dict[str, Any]],
    expire: int = 600
):
    """
    写入新闻列表缓存
    """
    
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)

async def get_cached_news_list(
    category_id: Optional[int],
    page: int,
    size: int
):
    """ 
    获取新闻列表缓存
    """
    
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)

