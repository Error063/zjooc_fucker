from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Input, ListView, Header, Static
from textual.binding import Binding

username = ""


class InformationForm(Static):

    def compose(self) -> ComposeResult:
        yield Input(placeholder="your username")

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        global username
        username = event.value


class VideoApp(App):
    CSS_PATH = "tui.tcss"

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield InformationForm()
        yield Footer()


if __name__ == "__main__":
    VideoApp().run()
    print(username)
    with open('video.py', 'r') as code_file:
        code = code_file.read()

    exec(code)
