import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Activity


class CommandForward(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cnt = 1

    def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(
            'test_group',
            self.channel_name
        )
        self.accept()
        self.send("Who is that?")
        Activity.objects.filter(id=4).update(channel_name=self.channel_name)
        # print(self.channel_name)

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            'test_group',
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        self.send('sb')
        # self.send('{"action": "append-user", "content": {"avatar": "https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTL8dFCa5KPR7Td5rjB6sg41q0ajcIHFwFJMZicY6dSKd3fJhEIvclqX1QeiaJBZcbvVicGzticThdHiauA/132", "nickname": "Yeah...", "language": "zh_CN", "nickName": "Yeah...", "country": "China", "province": "Jilin", "gender": 1, "uid": "oxwbU5M0-CCKSRFknW16tv3JiC3M", "city": "Yanbian"}}')
        # self.send('{"action": "send-danmu", "content": {"danmu": "kao", "openid": "oxwbU5M0-CCKSRFknW16tv3JiC3M"}}')
        self.cnt += 1

    def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.

        self.send(text_data=event["text"])
