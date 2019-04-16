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
