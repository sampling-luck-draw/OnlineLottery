import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from MicroProgram.database_sync_to_async_functions import *
from MicroProgram.handler import Handler
from django.contrib.sessions.models import Session


class Console(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user', None)
        await self.accept()
        if user is None:
            try:
                cookies = dict(self.scope['headers'])[b'cookie']
                cookies_list = cookies.decode('utf-8').split(';')
                cookies_list = [a.strip() for a in cookies_list]
                cookies_dict = {a.split('=')[0]: a.split('=')[1] for a in cookies_list}
                sessionid = cookies_dict['sessionid']
                session = Session.objects.get(session_key=sessionid)
                session_data = session.get_decoded()
                uid = session_data.get('_auth_user_id')
                user = User.objects.get(id=uid)
            except Exception:
                pass

        if user is None or not user.is_authenticated:
            await self.send('{"error":"unauthenticated"}')
            await self.close()
            return

        organizer = await get_organizer(user)
        try:
            activity_id = self.scope['url_route']['kwargs'].get('activity_id', None)
        except KeyError:
            # FOR TEST ONLY
            try:
                activity_id = int(self.scope['query_string'].decode('utf-8').split('=')[1])
            except Exception:
                activity_id = None
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
        try:
            await self.channel_layer.group_discard(
                'console_' + str(self.activity.id),
                self.channel_name
            )
        except AttributeError:
            pass
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        try:
            message = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send('json decode error')
            return
        if not isinstance(message, dict):
            await self.send('json decode error')
            return
        #
        # if 'content' not in message:
        #     await self.send('no content')
        #     return

        method_name = 'handle_' + message['action'].replace('-', '_')
        print(method_name)
        if hasattr(Handler, method_name):
            method = getattr(Handler, method_name)
            await self.send(await method(self.handler, message))
        else:
            await self.send('unrecognized action {}'.format(message['action']))

    async def chat_message(self, event):
        # Handles the "chat.message" event when it's sent to us.
        await self.send(text_data=event["text"])
