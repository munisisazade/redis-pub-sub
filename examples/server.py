import os
from redisrpc import RedisRPC

# Add REDIS_URI application enviroment

os.environ.setdefault("REDIS_URI", "redis://localhost:6379/0")

rpc = RedisRPC("channel_name")  # rename what you want


# event lists
def calc_square(response):  # `response` is a sender data
    power_of_number = response**2

    return power_of_number  # sent to client


def calc_cube(response):  # `response` is a sender data
    cube_of_number = response**3
    return cube_of_number  # sent to client


rpc.register(calc_square, "square")  # event name default function name
rpc.register(calc_cube)

rpc.listen()
