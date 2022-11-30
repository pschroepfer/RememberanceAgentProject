from kivy.app import App
from kivy.lang import Builder

kv = """
Screen:
    BoxLayout:
        spacing: 10
        orientation: "vertical"

        ScrollView:
            id: scroll_view
            always_overscroll: False
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                Label:
                    id: label
                    size_hint: None, None
                    size: self.texture_size 

        Button:
            text: "Add Text"
            size_hint_y: 0.2
            on_release: app.add_text()

"""


class TextAdding(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_counter = 0

    def build(self):
        return Builder.load_string(kv)

    def add_text(self):
        self.root.ids.label.text += f"Remembrance Agent Live Stream {self.text_counter}\n"
        self.text_counter += 1
        self.root.ids.scroll_view.scroll_y = 0


if __name__ == "__main__":
    TextAdding().run()