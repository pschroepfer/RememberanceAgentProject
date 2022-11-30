from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
import asynckivy as ak

class MyBotLayout(TabbedPanel):

    def pressStart(self):
        self.bot_start.disabled = True
        self.spider_status.text = "Running"
        
        # How to kill this async function below?
        async def scraper(self):
            while 1:
                # do something until break
                if break_condition_met:
                    break
        my_task = ak.start(scraper(self))
        my_task.cancel()




class MyBotApp(App):
    def build(self):
        return MyBotLayout()

MyBotApp().run()