import os
from redisrpc import RedisRPC
# Add REDIS_URI application enviroment

os.environ.setdefault("REDIS_URI", "redis://localhost:6379/0")

pub = RedisRPC("channel_name") # channel name must be same as listener
square = pub.send("square", 5) # send data to spesific event
cube = pub.send("cube", 3)

# response from server handlers
print(square) # 25
print(cube) # 27

