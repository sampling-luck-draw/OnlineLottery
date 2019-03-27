from channels.generic.websocket import WebsocketConsumer
from .models import Activity


class CommandForward(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cnt = 1

    def connect(self):
        self.accept()
        self.send("Who is that?")
        Activity.objects.filter(id=4).update(channel_name=self.channel_name)
        # print(self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        self.send("Oh " + text_data + " " + str(self.cnt))
        self.cnt += 1

    def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        self.send(text_data=event["text"])
