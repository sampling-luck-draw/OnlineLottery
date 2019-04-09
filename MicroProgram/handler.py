import json

from MicroProgram.database_sync_to_async_functions import *
from Pages.utils import model_to_json


class Handler:
    def __init__(self, activity):
        self.activity = activity

    async def handle_luck_dog(self, message):
        uid = message['content']['uid']
        award_name = message['content']['award']
        await add_lucky_dog(self.activity, uid, award_name)
        return '{"result": "success"}'

    async def handle_append_award(self, message):
        award_name = message['content']['name']
        prize_name = message['content']['prize']
        amount = message['content']['amount']
        await add_award(self.activity, award_name, prize_name, amount)
        return '{"result": "success"}'

    async def handle_modify_activity(self, message):
        return 'handle_modify_activity'

    async def handle_get_participants(self, message):
        participants = await get_participants_by_activity(self.activity)
        participants_list = [model_to_json(i) for i in participants]

        return json.dumps({'action': 'participants', 'content': participants_list})
