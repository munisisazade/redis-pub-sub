import os
import time
import base64
import json
import uuid
import platform
import itertools
import datetime
import traceback
from urllib.parse import urlparse
from redisrpc.version import VERSION
from redisrpc.errors import ChannelActiveException

try:
    import redis
except ImportError:
    raise ImportError("redis package must be installed")


class BasePubSub(object):
    """
    Base publish–subscribe is a
    messaging pattern class
    """

    def __init__(self, channel_name):
        """
        Initialize and subscribe channel
        """
        self.validate_env()
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

    def validate_env(self):
        if not os.getenv("REDIS_URI"):
            raise ValueError("REDIS_URI environment variable must be set")

    def check_before_connect(self):
        # Get the list of currently active channels
        active_channels = self.rdb.pubsub_channels()
        if self.channel.encode("utf-8") in active_channels:
            print("Please use different channel name or kill existing channel")
            raise ChannelActiveException(self.channel)

    def listen(self):
        self.check_before_connect()
        try:
            self.print_start()
            self.log_print("Pubsub is listen...")
            self.pubsub.subscribe(self.channel)
            while True:
                message = self.pubsub.get_message()
                if message:
                    if message["type"] == "message":
                        data = self.__convert_to_python(message["data"])
                        if data["token"] != self.token:
                            self.log_print("new request", type="DEBUG")
                            event_name = data["event_name"]
                            response_data = data["data"]
                            self.event_handler(event_name, response_data)
                time.sleep(0.3)
        except KeyboardInterrupt:
            self.log_print("Pubsub is stoping...")
            time.sleep(1)
            self.log_print("Shutdown")

    def event_handler(self, event_name, data):
        if self.events.get(event_name, False):
            event = self.events.get(event_name)
            try:
                response = event(data)
                if response:
                    self.log_print(f"Success response from {event_name}", "DEBUG")
                    self.__send_reponse(
                        {
                            "token": self.token,
                            "event_name": event_name,
                            "data": response,
                        }
                    )
                else:
                    self.log_print(f"Empty response from {event_name}", "WARNING")
            except:
                self.log_print(traceback.format_exc(), "FATAL")
        else:
            self.log_print(f"Can't find `{event_name}` event name", "ERROR")
            return {"error": f"Can't find `{event_name}` event name"}

    def print_start(self):
        start_text = f"""
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis Publish–subscribe Remote Procedure Call system
  .-`` .-```.  ```\/    _.,_ ''-._      Connection: {self.connection_uri()}                             
 (    '      ,       .-`  | `,    )     Channel name: {self.channel} 
 |`-._`-...-` __...-.``-._|'` _.-'|     Channel token: {self.token}
 |    `-._   `._    /     _.-'    |     Hostname: {platform.node()}
  `-._    `-._  `-./  _.-'    _.-'      Running                             
 |`-._`-._    `-.__.-'    _.-'_.-'|     PID: {os.getpid()}                             
 |    `-._`-._        _.-'_.-'    |     Name: RedisPubSub {VERSION}v        
  `-._    `-._`-.__.-'_.-'    _.-'            https://github.com/munisisazade/redis-pub-sub                             
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                   
"""
        print(start_text)
        print("[events]")
        start_count = itertools.count(1)
        for event_name in self.events.keys():
            print(f"{next(start_count)})", event_name)
        print("")
        self.log_print("Starting...")

    def log_print(self, text, type="INFO"):
        now = datetime.datetime.today()
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%f')}: {type}] {text}")

    def connection_uri(self):
        uri = urlparse(os.getenv("REDIS_URI"))
        host = uri.netloc
        if ":" in host and "@" in host:
            paswd = host[host.index(":") : host.index("@")]
            return os.getenv("REDIS_URI").replace(paswd, "***")
        else:
            return os.getenv("REDIS_URI")

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
        resp = {"token": self.token, "event_name": event_name, "data": data}
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
