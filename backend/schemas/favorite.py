from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from schemas.base import NewsItemBase

class FavoriteCheckResponse(BaseModel):
    """收藏状态响应"""
    is_favorite: bool = Field(..., description="isFavorite")
    
class FavoriteAddRequest(BaseModel):
    """收藏添加"""
    news_id: int = Field(..., description="news_id")
    
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )
    
class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., description="hasMore")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )