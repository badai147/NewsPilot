from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class UserRequest(BaseModel):
    username: str
    password: str
    
class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserInfoResponse(UserInfoBase):
    """
    用户信息返回数据模型
    """
    id: int
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class UserAuthResponse(BaseModel):
    """
    认证相应
    """
    
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")
    
    # 模型类配置
    model_config = ConfigDict(
       populate_by_name=True,
       from_attributes=True
    )

class UserUpdateRequest(BaseModel):
    """
    用户更新数据模型
    """
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None

class UserChangePasswordRequest(BaseModel):
    """
    用户修改密码数据模型
    """
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")