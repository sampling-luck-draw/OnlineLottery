import json

from channels.generic.websocket import AsyncWebsocketConsumer
from MicroProgram.database_sync_to_async_functions import *
from MicroProgram.handler import Handler


class Console(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope['user']
        await self.accept()
        if not user.is_authenticated:
            await self.send('{"error":"unauthenticated"}')
            await self.close()
            return

        organizer = await get_organizer(user)
        activity_id = self.scope['url_route']['kwargs'].get('activity_id', None)
        if not activity_id:
            activity = await get_latest_activity(organizer)
            if not activity:
                await self.send('{"error":"no available activity"}')
                await self.close()
                return
        else:
            try:
                activity = await get_activity_by_id(activity_id)
            except models.Activity.DoesNotExist:
                await self.send('{"error":"invalid activity id"}')
                await self.close()
                return
        self.activity = activity
        self.handler = Handler(activity)

        await self.channel_layer.group_add(
            'console_' + str(activity.id),
            self.channel_name
        )
        await self.send("BLXDNZ")
        # print(self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            'console_' + str(self.activity.id),
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send('json decode error')
            return

        method_name = 'handle_' + message['action'].replace('-', '_')
        if hasattr(Handler, method_name):
            method = getattr(Handler, method_name)
            await self.send(await method(self.handler, message))
        else:
            await self.send('unrecognized action {}'.format(message['action']))

    async def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        await self.send(text_data=event["text"])
