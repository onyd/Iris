from typing import Iterable
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivy.properties import StringProperty

from Iris.GUI.Behavior import SelectDragBehavior, AntiCollisionObject
from Iris.utils.Utils import Utils
from Iris.utils.Structures.XAbleObject import SerializableObject, ExecutableObject


class Component(SelectDragBehavior, BoxLayout, SerializableObject,
                ExecutableObject, AntiCollisionObject):
    icon = StringProperty("message_bubble.png")

    def __init__(self, settings=None, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.mode = None
        self.max_output = 0

        self.register_event_type("on_add_link")
        self.register_event_type("on_remove_link")

    def setup_gui(self, *args):
        super().setup_gui(*args)

        self.bind(size=lambda x, y: self.draw_selection_box())

    def __call__(self, buffer, **kwargs):
        pass

    def selection_mode(self, igniter, mode):
        self.mode = mode
        self.selection_frame_color = (0., 1., 0., 1.)
        self.sdb_enabled = False

        # the current selected componet will be pre selected
        if self.selected:
            igniter.pre_selected = self
            self.draw_selection_box()

    def edit_mode(self, igniter, mode):
        self.mode = mode
        self.sdb_enabled = True
        self.unselect()
        self.selection_frame_color = (0., 0., 0., 1.)

    # Event
    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos) and self.mode:
            # add/remove link if predecessor exist or add it and wait for a second touch
            if self.mode == "add_link":
                self.dispatch("on_add_link", self)

            elif self.mode == "remove_link":
                self.dispatch("on_remove_link", self)

        return super().on_touch_down(touch)

    def on_add_link(self, *args):
        pass

    def on_remove_link(self, *args):
        pass

    def to_dict(self, **kwargs):
        return super().to_dict(pos=self.pos, **kwargs)


class StartComponent(Component):
    pass