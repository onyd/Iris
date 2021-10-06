from kivy.uix.label import Label
from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder
from kivy.graphics.svg import Svg
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.label import MDLabel

from Iris.core.Models.Components.Actions import *
from Iris.GUI.Widgets import *
from Iris.GUI.Screen import *
from Iris.GUI.Behavior import *


class TestApp(MDApp):
    def build(self):
        self.layout = FloatLayout()
        self.area = GrabableGrid(do_rotation=False)
        self.layout.add_widget(self.area)

        return self.layout  #Builder.load_file(r"Iris/GUI/KV/test.kv")


TestApp().run()
