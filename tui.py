import json
from textual.app import App, ComposeResult
from textual.widgets import Footer, Input, Header, Static, Button

# 用户信息
user_information: dict = {"username": "", "password": "", "totalPage": 1}


class InformationForm(Static):

    def __init__(self, close_app_function) -> None:
        super().__init__()
        # 关闭APP的函数
        self.close_app_function = close_app_function

    def compose(self) -> ComposeResult:
        yield Input(placeholder="your username", id="username")
        yield Input(placeholder="your password", id="password")
        yield Button("Start", variant="success", id="Start")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "username":
            user_information["username"] = event.value
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


if __name__ == "__main__":
    VideoApp().run()
    # 运行刷课代码
    with open('video.py', 'r') as code_file:
        code = code_file.read()
    exec(code)
