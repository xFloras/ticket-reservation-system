import redis.asyncio as Redis

redis_client = Redis.from_url("redis://localhost:6379", decode_responses=True)

async def set_seat_lock(event_id: int, seat_id: int, user_id: int, expiration: int = 600):
    key = f"event_{event_id}:seat_{seat_id}"
    return await redis_client.set(key, user_id, ex=expiration, nx=True)

async def release_seat_lock(event_id: int, seat_id: int, user_id: int):
    key = f"event_{event_id}:seat_{seat_id}"
    current_user_id = await redis_client.get(key)
    if current_user_id == str(user_id):
        await redis_client.delete(key)
        return True
    return False

async def get_seat_status(event_id: int, seat_id: int):
    key = f"event_{event_id}:seat_{seat_id}"
    return await redis_client.get(key)