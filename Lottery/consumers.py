from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ServiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_pk = self.scope['url_route']['kwargs']['project_pk']
        self.room_group_name = 'status_%s' % self.project_pk
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'status_message',
                'message': message
            }
        )

    # Receive message from room group
    async def status_message(self, event):
        # todo: get real status from service detection api
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
