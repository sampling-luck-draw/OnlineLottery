from channels.generic.websocket import WebsocketConsumer


class CommandForward(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cnt = 1

    def connect(self):
        self.accept()
        self.send("Who is that?")

    def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        self.send("Oh " + text_data + " " + str(self.cnt))
        self.cnt += 1
