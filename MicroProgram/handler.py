import json

from MicroProgram.database_sync_to_async_functions import *
from Pages.utils import model_to_json, utc_to_local


class Handler:
    def __init__(self, activity):
        self.activity = activity

    async def handle_lucky_dog(self, message):
        uid = message['content']['uid']
        award_name = message['content']['award']
        result = await add_lucky_dog(self.activity, uid, award_name)
        if result is None:
            return '{"result": "success"}'
        else:
            return '{"error": "' + result + '"}'

    async def handle_append_award(self, message):
        award_name = message['content']['name']
        prize_name = message['content']['prize']
        amount = message['content']['amount']
        await add_award(self.activity, award_name, prize_name, amount)
        return '{"result": "success"}'

    async def handle_delete_award(self, message):
        award_name = message['content']['name']
        await delete_award(self.activity, award_name)
        return '{"result": "success"}'

    async def handle_modify_activity(self, message):
        await modify_activity(self.activity, message['content'])
        return '{"result": "success"}'

    async def handle_get_participants(self, message):
        participants = await get_participants_by_activity(self.activity)
        # participants_list = [model_to_json(i) for i in participants]
        participants_list = []
        for x in participants:
            j = model_to_json(x)
            j['uid'] = j['openid']
            del j['openid']
            participants_list.append(j)
        return json.dumps({'action': 'participants', 'content': participants_list})

    async def handle_append_user(self, message):
        content = message['content']
        await add_participant(content, self.activity)
        return '{"result": "success"}'

    async def handle_get_activity_info(self, message):
        data = {
            'name': self.activity.name,
            'start_time': utc_to_local(self.activity.start_time).strftime("%Y-%m-%d %H:%M:%S")
            if self.activity.start_time else "未开始",
            'end_time': utc_to_local(self.activity.end_time).strftime("%Y-%m-%d %H:%M:%S")
            if self.activity.end_time else "未结束",
            'invite_code': id_to_invite_code(self.activity.id)
        }
        return json.dumps({'action': 'activity-info', 'content': data})

    async def handle_get_awards(self, message):
        awards = await get_awards_by_activity(self.activity)
        awards_list = [model_to_json(i) for i in awards]
        return json.dumps({'action': 'awards', 'content': awards_list})

    async def handle_get_lucky_dogs(self, message):
        dogs = await get_lucky_dogs_by_activity(self.activity)
        return json.dumps({'action': 'lucky-dogs', 'content': json.dumps(dogs)})
