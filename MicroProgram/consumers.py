import json

from channels.generic.websocket import AsyncWebsocketConsumer
from MicroProgram import models
from MicroProgram.database_sync_to_async_functions import *


class Console(AsyncWebsocketConsumer):

    async def handle_luck_dog(self, message):
        uid = message['content']['uid']
        await self.send('handle_luck_dog')

    async def handle_modify_activity(self, message):
        await self.send('handle_modify_activity')

    async def handel_get_participants(self, message):
        await self.send('handel_get_participants')

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.send('{"error":"unauthenticated"}')
            await self.close()
            return
        await self.accept()

        organizer = await get_organizer(user)
        activity_id = self.scope['url_route']['kwargs'].get('activity_id', None)
        if not activity_id:
            activity = await get_latest_activity(organizer)
        else:
            try:
                activity = await get_activity_by_id(activity_id)
            except models.Activity.DoesNotExist:
                await self.send('invalid id')
                return
        self.activity = activity

        await self.channel_layer.group_add(
            'console_' + str(activity.id),
            self.channel_name
        )
        await self.send("BLXDNZ")
        # print(self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            'console_' + self.activity.id,
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
        await self.send(method_name)
        if hasattr(Console, method_name):
            method = getattr(Console, method_name)
            await method(self, message)
        else:
            await self.send('unrecognized action {}'.format(message['action']))

    async def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        await self.send(text_data=event["text"])
