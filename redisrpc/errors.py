class Handler(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


class ChannelActiveException(Exception):
    def __init__(self, channel):
        self.channel = channel
        super().__init__(f"Channel '{channel}' is currently active.")
