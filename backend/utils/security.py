from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_password(password: str):
    # 密码加密
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    # 密码验证
    return pwd_context.verify(plain_password, hashed_password)
