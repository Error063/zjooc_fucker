import hashlib
import random
import time


def generateRandomStringWithTimestamp(length):
    return ''.join(random.choice("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678")) + str(time.time() * 1000)


def calculateMd5():
    return hashlib.md5(f"{str(int(time.time() * 1000))}gxpt_lanao".encode()).hexdigest()