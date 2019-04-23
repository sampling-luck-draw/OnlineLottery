import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from MicroProgram.models import *


def send_danmu(participant, content):
    danmu = Danmu()
    danmu.sender = participant
    danmu.text = content
    danmu.time = datetime.datetime.now()
    try:
        danmu.activity = Activity.objects.get(id=danmu.sender.activate_in)
    except Activity.DoesNotExist:
        return False
    danmu.save()

    channel_layer = get_channel_layer()

    print('channel name: ' + 'console_' + str(danmu.sender.activate_in))
    async_to_sync(channel_layer.group_send)(
        'console_' + str(danmu.sender.activate_in),
        {
            'type': 'chat.message',
            'text': json.dumps(
                {'action': 'send-danmu', 'content': {'uid': participant.openid,
                                                     'danmu': content}})
        }
    )
    return True
