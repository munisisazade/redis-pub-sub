# redis-pub-sub

Redis RPC with PubSub simple lightweight

# Getting Started

### Listener interface example
```python
import os
from redispubsub import RedisRPC
# Add REDIS_URI application enviroment

os.environ.setdefault("REDIS_URI", "redis://localhost:6379/0")

rpc = RedisRPC("channel_name") # rename what you want

def calc_square(response): # `response` is a sender data
    power_of_number = response**2
    return power_of_number # sent to client
    
def calc_cube(response): # `response` is a sender data
    power_of_number = response**2
    return power_of_number # sent to client

rpc.register(calc_square, "square") # event name default function name
rpc.register(calc_cube, "cube")

rpc.listen()
```
### Client interface
```python
from redispubsub import RedisRPC
# Add REDIS_URI application enviroment

os.environ.setdefault("REDIS_URI", "redis://localhost:6379/0")

pub = RedisRPC("channel_name") # channel name must be same as listener
square = pub.send("square", 5) # send data to spesific event 
cube = pub.send("cube", 3) 

print(square) # 25
print(cube) # 27
```

# Contributing
Fell free to open issue and send pull request.
