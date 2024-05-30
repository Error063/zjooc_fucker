import json
from textual.app import App, ComposeResult
from textual.widgets import Footer, Input, Header, Static, Button

from fkzjooc import API
from constants import *

# 用户信息
user_information: dict = {"account": "", "password": "", "totalPage": 1}


class InformationForm(Static):

    def __init__(self, close_app_function) -> None:
        super().__init__()
        # 关闭APP的函数
        self.close_app_function = close_app_function

    def compose(self) -> ComposeResult:
        yield Input(placeholder="your account", id="account", type="text")
        yield Input(placeholder="your password", id="password", type="text")
        yield Button("Start", variant="success", id="Start")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "account":
            user_information["account"] = event.value
        elif event.input.id == "password":
            user_information["password"] = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "Start":
            # 用户信息写入文件
            with open("account.json", "w") as file:
                json.dump(user_information, file)
            # 关闭app
            self.close_app_function()


class VideoApp(App):
    CSS_PATH = "tui.tcss"

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield InformationForm(self.exit)
        yield Footer()


def finish_video(api: API):
    # 打印json格式的课程信息
    course_list: dict = api.get_user_course_list()
    if course_list["success"] == True:
        for course in course_list["data"]:
            print(">" + course["name"])
            # 获取课程的章节
            course_chapter: dict = api.get_course_chapter_list(course["id"])
            if course_chapter["success"] == True:
                # 找到每个章节
                for chapter in course_chapter["data"]:
                    print("|--" + chapter["name"])
                    # 找到每个小节
                    for lesson in chapter["children"]:
                        print("|----" + lesson["name"])
                        # 找到小节的视频任务
                        for task in lesson["children"]:
                            print("|--------" + task["name"])
                            task_id = task["id"]
                            try:
                                api.send_course_finish_request(
                                    course["id"], task_id, -1)
                            except Exception as e:
                                print(e)
                                print(task["name"] + "failed")


if __name__ == "__main__":
    VideoApp().run()
    # 运行刷课代码
    account = ""
    password = ""
    with open('account.json') as account_information_file:
        account_information = json.load(account_information_file)
        account = account_information['account']
        password = account_information['password']
        total_page = account_information['totalPage']

    # 创建一个API对象
    api = API(account, password)

    # 刷视频
    finish_video(api)
