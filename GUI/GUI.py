from Iris.Config.SettingsManager import SettingsManager
from Iris.GUI.Screen import *
from Iris.GUI.Widgets import *
from kivymd.uix.toolbar import MDToolbar
from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')


class MainApp(MDApp):
    def build(self):
        self.settings = SettingsManager()

        # Setup tool bar
        self.tool_bar = MDToolbar(elevation=8)
        self.tool_bar.left_action_items.append(["menu", lambda x: x])
        self.tool_bar.right_action_items.append(["magnify", lambda x: x])

        self.screen_manager = Builder.load_file(r"Iris/GUI/KV/main.kv")

        self.layout = GridLayout(cols=1)
        self.layout.add_widget(self.tool_bar)
        self.layout.add_widget(self.screen_manager)

        return self.layout

    def set_home_tool_bar(self):
        self.tool_bar.left_action_items = [["menu", lambda x: x]]
        self.tool_bar.right_action_items = [["magnify", lambda x: x]]

    def set_lab_tool_bar(self):
        self.tool_bar.left_action_items = [[
            'arrow-left', lambda x: self.change_screen("choose_editor_screen")
        ]]
        self.tool_bar.right_action_items = []

    def set_disabled_tool_bar(self, callback=None):
        left_items = self.tool_bar.left_action_items[:]
        right_items = self.tool_bar.right_action_items[:]

        def back_to_tool_bar(left, right):
            self.tool_bar.left_action_items = left
            self.tool_bar.right_action_items = right

            if callback:
                callback()

        self.tool_bar.left_action_items = [[
            'arrow-left', lambda x: back_to_tool_bar(left_items, right_items)
        ]]
        self.tool_bar.right_action_items = []

    def change_screen(self, name):

        if name == "choose_editor_screen":  # to modify: do these things in on_pre_enter/leave function
            # reset tool_bar
            self.set_home_tool_bar()

            self.screen_manager.current = 'home_screen'
        else:
            # Modify tool bar
            self.set_lab_tool_bar()

            # Change screen
            self.screen_manager.current = name

    def send_message(self):
        scrollable_message = self.screen_manager.ids[
            'conversations_screen'].ids['scrollable_message']
        message = self.screen_manager.ids['conversations_screen'].ids[
            'message_field']

        if message.text != "":
            scrollable_message.append_message(message.text)
            message.text = ""


MainApp().run()

