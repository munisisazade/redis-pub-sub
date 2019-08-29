import redis
import os
import time
import base64
import json


class BasePubSub(object):
    """
        Base publish–subscribe is a
        messaging pattern class
    """

    def __init__(self, channel_name):
        """
            Initialize and subscribe channel
        """
        self.rdb = redis.StrictRedis.from_url(os.getenv("REDIS_URI"))
        self.channel = channel_name
        self.pubsub = self.rdb.pubsub()
        self.pubsub.subscribe(channel_name)
        self.events = {}

    def listen(self):
        print("Pubsub is listen...")
        while True:
            message = self.pubsub.get_message()
            if message:
                if message["type"] == "message":
                    data = self.__convert_to_python(message["data"])
                    event_name = data["event_name"]
                    response_data = data["data"]
                    self.event_handler(event_name, response_data)
            time.sleep(0.3)

    def event_handler(self, event_name, data):
        if self.events.get(event_name, False):
            event = self.events.get(event_name)
            response = event(data)
            if response:
                self.__send_reponse({
                    "event_name": event_name,
                    "data": data
                })
                # self.

    def __encode_base64(self, data):
        return base64.b64encode(json.dumps(data).encode("utf-8"))

    def __convert_to_python(self, byte):
        if isinstance(byte, bytes):
            response = base64.b64decode(byte).decode("utf-8")
            return json.loads(response)
        elif isinstance(byte, int):
            return byte
        else:
            raise TypeError(
                f"a bytes-like object is required, not '{type(byte).__name__}'"
            )

    def register(self, name, function):
        if callable(function):
            self.events[name] = function
        else:
            raise ValueError("Event function must be callable object")

    def __send_reponse(self, data):
        decode = self.__encode_base64(data)
        self.rdb.publish(self.channel, decode)

    def send(self, event_name, data):
        resp = {
            "event_name": event_name,
            "data": data
        }
        decode = self.__encode_base64(resp)
        self.rdb.publish(self.channel, decode)
        print("Send")


f = {
    "event_name": "handler",
    "data": {
        "a": 21
    }
}
