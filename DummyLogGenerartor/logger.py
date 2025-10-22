#!/opt/demo-logger/venv/bin/python
from loguru import logger
import time, json, random, string, os

os.makedirs("/var/log/demoapp", exist_ok=True)

logger.add("/var/log/demoapp/app.log",
           rotation="10 MB",
           retention="3 days",
           compression="gz",
           enqueue=True,
           format="{time:YYYY-MM-DDTHH:mm:ss.SSS} | {level:<7} | {message}")

levels    = ["DEBUG","INFO","WARNING","ERROR"]
endpoints = ["/login","/pay","/search","/orders","/items"]
users     = ["alice","bob","carol","dan","erin"]

def rid(n=8): 
    return "".join(random.choices(string.ascii_letters+string.digits, k=n))

while True:
    evt = {
        "event": "request",
        "id": rid(),
        "user": random.choice(users),
        "endpoint": random.choice(endpoints),
        "latency_ms": random.randint(5, 1200),
        "ok": random.choice([True, True, True, False])
    }
    lvl = random.choice(levels)
    # JSON line (easy to parse later)
    logger.log(lvl, json.dumps(evt))
    # Human-friendly line
    logger.log(lvl, f"{evt['user']} -> {evt['endpoint']} in {evt['latency_ms']}ms ok={evt['ok']}")
    time.sleep(random.uniform(0.2, 1.5))
