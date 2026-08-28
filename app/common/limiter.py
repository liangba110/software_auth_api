from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config.settings import settings

# 使用Redis作为限流后端
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)
