import os
import json
import redis
from dotenv import load_dotenv

def read_redis_logs():
    load_dotenv()
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("REDIS_URL not found")
        return

    try:
        r = redis.from_url(redis_url, decode_responses=True)
        logs = r.lrange("agent_logs", 0, 100)
        print(f"Lendo {len(logs)} logs do Redis...")
        for log_str in logs:
            try:
                log = json.loads(log_str)
                print(f"[{log.get('timestamp')}] {log.get('message')}")
            except:
                print(log_str)
    except Exception as e:
        print(f"Erro ao conectar no Redis: {e}")

if __name__ == "__main__":
    read_redis_logs()
