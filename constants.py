import time

# 请求头
HEADERS: dict = {
    "Accept":
    "application/json, text/javascript, */*; q=0.01",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/111.0.0.0 Safari/537.36",
}

# login page
# URL参数常量
APP_KEY: str = '1ddadc7d-6f0a-4eb0-b844-24dd28e33e74'
LOGIN_PAGE_URL = "https://centro.zjlll.net/ajax"
LOGIN_PAGE_PARAMETERS: dict = {
    "time": time.time() * 1000,
    "service": "/centro/api/authcode/create",
    "params": ''
}
