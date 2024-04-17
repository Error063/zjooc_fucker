import hashlib
import random
import time


from dateutil.parser import parse
import datetime

def convertToUnixTimestamp(dateTimeString):
    date_time_obj = parse(dateTimeString)
    utc_date_time_obj = date_time_obj.astimezone(datetime.timezone.utc)
    unix_timestamp = (utc_date_time_obj - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()

    return unix_timestamp


def generateRandomStringWithTimestamp(length):
    return ''.join(random.choice("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678")) + str(time.time() * 1000)


def calculateMd5():
    return hashlib.md5(f"{str(int(time.time() * 1000))}gxpt_lanao".encode()).hexdigest()