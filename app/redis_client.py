import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def set_seat_lock(event_id: int, seat_id: int, user_id: int, expiration: int = 600):
    key = f"event_{event_id}:seat_{seat_id}"
    return redis_client.set(key, user_id, ex=expiration, nx=True)

def release_seat_lock(event_id: int, seat_id: int, user_id: int):
    key = f"event_{event_id}:seat_{seat_id}"
    current_user_id = redis_client.get(key)
    if current_user_id == str(user_id):
        redis_client.delete(key)
        return True
    return False

def get_seat_status(event_id: int, seat_id: int):
    key = f"event_{event_id}:seat_{seat_id}"
    return redis_client.get(key)