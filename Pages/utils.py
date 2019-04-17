import datetime
import json


def to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=False, indent=0)


def model_to_json(obj):
    l = [(k, v) for k, v in obj.__dict__.items() if k[0] != '_']
    return dict(l)


def utc_to_local(utc_dt):
    # if isinstance(utc_dt, str):
    #     utc_dt = datetime.datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
    # TODO: **Important** Dynamic time zone
    # return utc_dt.astimezone(tz=pytz.timezone(settings.TIME_ZONE))
    return utc_dt + datetime.timedelta(hours=8)


def local_to_utc(local_dt):
    return local_dt - datetime.timedelta(hours=8)

# r = "ACDEFHKLPRSTWXY"
r1 = 'HAFREYPDK'
r2 = 'LTDKXECRF'
r3 = 'XKCSLREYW'
r4 = 'KRXPCHATF'
r5 = 'AXLCDTHKE'
def id_to_invite_code(i):
    return r1[i / 10000] + r2[i / 1000] + r3[i / 100] + r2[i / 10] + r5[i % 10]

def invite_code_to_i(code):
    return r1.find(code[0]) * 10000 + r2.find(code[1]) * 1000 + \
           r3.find(code[2]) * 100 + r4.find(code[3]) * 10 + r5.find(code[4])