import redis
from app.config import Config

redis_client = redis.Redis(
    host='redis',
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True
)