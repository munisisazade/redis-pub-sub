from base import BasePubSub
from dotenv import load_dotenv

load_dotenv()

pub = BasePubSub("testing")


def handler(data):
    a = data.get("a")
    c = a * 7
    print(c)
    return c


pub.register("vurma", handler)

pub.listen()
