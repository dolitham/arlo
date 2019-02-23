import pandas as pd


def now():
    return pd.datetime.now()


def string_to_datetime(date):
    return pd.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')


def angular_string_to_timestamp(date):
    timestamp = pd.to_datetime(date).timestamp()
    now = now()
    hour_offset = 3600 * (now.hour) + 60 * (now.minute) + (now.second)
    return 1000 * (timestamp + hour_offset)


def lunchr_date_to_datetime(date):
    return pd.datetime.strptime(date[:-10], '%Y-%m-%dT%H:%M:%S')


def time_since(date):
    return now() - date


def get_timestamp_now():
    return pd.datetime.timestamp(now())


def timestamp_to_datetime(timestamp):
    return pd.datetime.fromtimestamp(int(timestamp)/1000)


def date_to_cycle(date):
    month = str(date.month_name())
    year = str(date.year)

    # TODO Overrule default dates to cycles

    return month[:3]+year[-2:]


def date_now():
    return pd.to_datetime('today')


def decode_cycle(cycle):
    if cycle == 'now':
        return date_to_cycle(date_now())
    return cycle
