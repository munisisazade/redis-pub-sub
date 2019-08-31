import os
import time
import base64
import json
import uuid

try:
    import redis
except:
    pass


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
        self.check_connection_redis()
        self.channel = channel_name
        self.pubsub = self.rdb.pubsub()
        self.events = {}
        self.token = str(uuid.uuid4())

    def check_connection_redis(self):
        try:
            self.rdb.set("testing", 1)
            assert int(self.rdb.get("testing")) == 1
            self.rdb.delete("testing")
        except:
            raise PermissionError(
                "Cannot read write redis database bellow credentials\n"
                f"redis_uri: {os.getenv('REDIS_URI')}"
            )

    def listen(self):
        print("Pubsub is listen...")
        self.pubsub.subscribe(self.channel)
        while True:
            message = self.pubsub.get_message()
            if message:
                if message["type"] == "message":
                    data = self.__convert_to_python(message["data"])
                    if data["token"] != self.token:
                        print("Yes")
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
                    "token": self.token,
                    "event_name": event_name,
                    "data": response
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

    def register(self, function, name=None):
        name = name if name else function.__name__
        if callable(function):
            self.events[name] = function
        else:
            raise ValueError("Event function must be callable object")

    def __send_reponse(self, data):
        decode = self.__encode_base64(data)
        self.rdb.publish(self.channel, decode)

    def send(self, event_name, data, wait_response_time=2):
        resp = {
            "token": self.token,
            "event_name": event_name,
            "data": data
        }
        decode = self.__encode_base64(resp)
        self.rdb.publish(self.channel, decode)
        print("Send")
        send_time = time.time()
        self.pubsub.subscribe(self.channel)
        while True:
            message = self.pubsub.get_message()
            if message:
                if message["type"] == "message":
                    data = self.__convert_to_python(message["data"])
                    if data["token"] != self.token:
                        self.pubsub.unsubscribe(self.channel)
                        return data["data"]
            response_time = time.time()
            if int(response_time - send_time) > wait_response_time:
                print("Cannot get response from server handler")
                return None
