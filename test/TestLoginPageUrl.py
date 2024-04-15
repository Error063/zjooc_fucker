import requests
import time

Headers: dict = {
    "Accept":
    "application/json, text/javascript, */*; q=0.01",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/111.0.0.0 Safari/537.36",
}

parameters: dict = {
    "time": time.time() * 1000,
    "service": "/centro/api/authcode/create",
    "params": ''
}

URL = "https://centro.zjlll.net/ajax"

# 打印get请求返回值

if __name__ == '__main__':
    session = requests.session()
    response = session.get(URL, headers=Headers, params=parameters)
    print(response.text)
