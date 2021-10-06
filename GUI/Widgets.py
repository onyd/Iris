import keyboard
import numpy as np

from kivy.graphics.transformation import Matrix
from kivy.metrics import sp, dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import Scatter, ScatterLayout

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Canvas, Rectangle, Color, Line
from kivy.uix.modalview import ModalView

from kivy.properties import (
    StringProperty,
    ColorProperty,
    NumericProperty,
    DictProperty,
    ListProperty,
    ObjectProperty,
    BooleanProperty,
    DictProperty,
)

from kivy.clock import Clock
from kivy.animation import Animation

from kivymd.app import MDApp
from kivymd.uix.behaviors import (
    RectangularElevationBehavior,
    RectangularRippleBehavior,
    BackgroundColorBehavior,
)
from kivymd.theming import ThemableBehavior
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFloatingActionButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import (
    OneLineAvatarListItem,
    OneLineAvatarIconListItem,
    MDList,
    ImageLeftWidget,
    ILeftBodyTouch,
    IRightBodyTouch,
    BaseListItem,
)
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox

from Iris.core.Models.Components.Component import Component
from Iris.core.Models.Components.Actions import Print
from Iris.GUI.Behavior import (
    SelectDragBehavior,
    UndispatchButtonBehavior,
    UndispatchBehavior,
)

res_dir = "Iris/resources/icon/"


class Icon(Label):
    source = StringProperty(None, allownone=True)


class RectangleIconLabelButton(
        RectangularRippleBehavior,
        RectangularElevationBehavior,
        ButtonBehavior,
        BackgroundColorBehavior,
        BoxLayout,
):
    text = StringProperty("")
    source = StringProperty(None, allownone=True)
    frame_color = ColorProperty()
    frame_width = NumericProperty(3.0)
    image_size = ListProperty([36, 36])


class CapsuleButton(
        RectangularRippleBehavior,
        RectangularElevationBehavior,
        BackgroundColorBehavior,
        UndispatchButtonBehavior,
        BoxLayout,
):
    margin = NumericProperty(dp(8))
    frame_color = ColorProperty()
    frame_width = NumericProperty(3.0)


class Message(RelativeLayout):
    text = StringProperty("")
    icon = StringProperty(None, allownone=True)
    anchor_x = StringProperty("left")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get("text", "")
        self.icon = kwargs.get("icon", None)
        self.anchor_x = kwargs.get("anchor_x", "left")


class ScrollableMessage(ScrollView):

    # Methos called externally to add new message to the chat history
    def append_message(self,
                       text,
                       anchor_x="left",
                       icon=res_dir + "message_bubble.png"):
        message = Message(text=text, icon=icon, anchor_x=anchor_x)

        chat_history = self.ids["chat_history"]
        chat_history.add_widget(message)

        Clock.schedule_once(lambda x: self.update_size())

        self.scroll_to(self.ids["scroll_to"])

    def update_size(self):
        chat_history = self.ids["chat_history"]
        layout = self.ids["layout"]

        height = 0
        for message in chat_history.children:
            height += message.ids["message"].texture_size[1] + dp(12)

        layout.height = height
        chat_history.height = height


class CustomBubble(RelativeLayout):
    arrow_x = NumericProperty(0)
    arrow_width = NumericProperty(10)
    arrow_height = NumericProperty(20)


class SwitchBase(BoxLayout):
    text = StringProperty()
    font_size = NumericProperty(12)

    color = ColorProperty((0.4, 0.4, 0.4, 1))
    selected_color = ColorProperty(None, allownone=True)

    callback = ObjectProperty(lambda x: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not touch.is_mouse_scrolling:
            self.callback(self.text)

            if isinstance(self.parent, CustomSwitch):
                self.parent.switch(self)


class SwitchCursor(BoxLayout):
    current_color = ColorProperty()

    text = StringProperty()
    font_size = NumericProperty(12)

    anim_duration = NumericProperty(0.5)


class CustomSwitch(RelativeLayout):
    selected = ObjectProperty()
    spacing = NumericProperty(4)

    cursor = ObjectProperty()

    def switch(self, instance):
        self.selected = instance

        # Animation
        cursor_anim = Animation(
            pos=self.selected.pos,
            current_color=self.selected.selected_color,
            d=self.cursor.anim_duration,
            t="in_out_expo",
        )
        label_fade_anim = Animation(label_opacity=0,
                                    d=self.cursor.anim_duration / 4,
                                    t="in_out_expo")
        label_fade_anim.bind(on_complete=self.update_text)
        label_in_anim = Animation(label_opacity=1,
                                  d=self.cursor.anim_duration / 4,
                                  t="in_out_expo")

        anim = cursor_anim & (label_fade_anim + label_in_anim)
        anim.start(self.cursor)

    def update_cursor(self, *args):
        self.cursor.pos = self.selected.pos
        self.cursor.size = self.selected.size
        self.cursor.current_color = self.selected.selected_color
        self.update_text()

    def update_text(self, *args):
        self.cursor.text = self.selected.text

    def on_size(self, *args):
        i = 0
        n = len(self.children) - 1  # -1 for the cursor

        for child in reversed(self.children):
            child.size = self.width / n - self.spacing, self.height * 0.65

            if isinstance(child, SwitchCursor):
                self.cursor = child
            else:
                child.center = (
                    self.x + (2 * i + 1) * self.width / (2 * n),
                    self.center_y,
                )
                i += 1

        Clock.schedule_once(lambda x: self.update_cursor())


class Grid(FloatLayout):
    square_width = NumericProperty(20)
    line_width = NumericProperty(1)

    def draw_grid(self):
        self.canvas.clear()
        with self.canvas:

            Color(0.6, 0.6, 0.6, 1)
            for i in range(0, int(self.width) + 1, int(self.square_width)):
                # Vertical
                Line(
                    points=[
                        self.x + i, self.y, self.x + i, self.y + self.height
                    ],
                    width=self.line_width,
                )

            for j in range(0, int(self.width) + 1, int(self.square_width)):
                # Horizontal
                Line(
                    points=[
                        self.x, self.y + j, self.x + self.width, self.y + j
                    ],
                    width=self.line_width,
                )

            # Bigger
            Color(0.3, 0.3, 0.3, 1)
            for k in range(0, int(self.width) + 1, int(self.width / 3)):
                # Vertical
                Line(
                    width=2 * self.line_width,
                    points=[
                        self.x + k, self.y, self.x + k, self.y + self.height
                    ],
                )
                # Horizontal
                Line(
                    width=2 * self.line_width,
                    points=[
                        self.x, self.y + k, self.x + self.width, self.y + k
                    ],
                )


class GrabableGrid(ScatterLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid = Grid(
            size_hint=(None,
                       None))  # TODO back and reenter don't show the grid
        self.add_widget(self.grid)

        self.bind(size=self.update_grid)
        Clock.schedule_once(self.update_grid)
        Clock.schedule_once(self.to_center)

    def collide_point(self, x, y):
        x0, y0 = self.parent.to_local(self.parent.x, self.parent.y)
        x1, y1 = self.parent.to_local(self.parent.right, self.parent.top)

        if x > x0 and x < x1 and y > y0 and y < y1:
            return True

        else:
            return False

    def on_touch_up(self, touch):

        # Round coordinates to have "aimed positioning"
        if touch.grab_current is self:
            touch.ungrab(self)
            x = self.pos[0] / 10
            x = round(x, 0)
            x = x * 10
            y = self.pos[1] / 10
            y = round(y, 0)
            y = y * 10
            self.pos = x, y
            return super().on_touch_up(touch)

    def on_transform_with_touch(self, touch):
        # When there is translation change position of the grid to keep it in view
        view_center = self.to_local(self.parent.center_x, self.parent.center_y)
        self.from_center = (
            view_center[0] - self.grid.center_x,
            view_center[1] - self.grid.center_y,
        )
        if abs(self.from_center[0]) > self.grid.width / 3:
            if self.from_center[0] > 0:
                self.grid.x += self.grid.width / 3
            else:
                self.grid.x -= self.grid.width / 3

        if abs(self.from_center[1]) > self.grid.height / 3:
            if self.from_center[1] > 0:
                self.grid.y += self.grid.height / 3
            else:
                self.grid.y -= self.grid.height / 3

        self.grid.draw_grid()

    def on_touch_down(self, touch):

        if touch.is_mouse_scrolling:
            if touch.button == "scrolldown":
                # zoom in
                if self.scale < self.scale_max:
                    self._set_scale(self.scale * 1.1)
                    if self.scale > self.scale_max:
                        self.scale = self.scale_max

            elif touch.button == "scrollup":
                # zoom out
                if self.scale > self.scale_min:
                    self._set_scale(self.scale * 0.9)
                    if self.scale < self.scale_min:
                        self.scale = self.scale_min

        return super().on_touch_down(touch)

    def update_grid(self, *args):
        s = 3 * max(*self.size) / self.scale_min
        self.grid.size = s, s
        self.grid.draw_grid()

    def to_center(self, *args):
        self.center = self.parent.width / 2, self.parent.height / 2
        self.grid.center = self.width / 2, self.height / 2
        self.grid.draw_grid()


class Tab(FloatLayout, MDTabsBase):
    """Class implementing content for a tab."""


class ComponentMenuSheet(MDTabs):
    pass


class SheetView(ModalView, RectangularElevationBehavior,
                BackgroundColorBehavior):
    radius = ListProperty([
        0,
    ])

    def __init__(self, **kwargs):
        self.md_bg_color = MDApp.get_running_app().theme_cls.bg_light
        super().__init__(**kwargs)


class BindField(UndispatchBehavior, BoxLayout):
    spacing = NumericProperty(dp(6))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            self.open_editor()

    def open_editor(self):
        self.sheet_view = SheetView(
            size_hint=(0.9, 0.9),
            radius=[
                14,
            ],
        )
        self.sheet_layout = BoxLayout(orientation="vertical",
                                      spacing=self.spacing,
                                      size_hint=(0.95, 0.95))
        self.sheet_view.add_widget(self.sheet_layout)

        self.fields_layout = BoxLayout(orientation="vertical",
                                       spacing=self.spacing)
        self.sheet_layout.add_widget(self.fields_layout)

        validation_btn = MDRaisedButton(text="OK", pos_hint={"right": 1})
        self.sheet_layout.add_widget(validation_btn)
        validation_btn.bind(on_press=lambda x: self.sheet_view.dismiss())

        for child in self.children[::-1]:
            self.remove_widget(child)
            self.fields_layout.add_widget(child)

        # self.sheet_layout.height = self.sheet_layout.minimum_height
        # self.sheet_view.height = self.sheet_layout.height

        self.sheet_view.open()

        self.sheet_view.bind(on_pre_dismiss=self.update_fields)

    def update_fields(self, instance):
        for child in self.fields_layout.children[::-1]:
            self.fields_layout.remove_widget(child)
            self.add_widget(child)


class AnimatedImage(Image):
    """Image widget providing additionnal function to animate image assuming there shape is:
    -name: <prefix> (<frame_number>).png
    -format: png format
    -structure: all in the same folder which need to be add in the prefix
    """

    prefix = StringProperty("image")
    loop = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.complete = True
        self.remaining_time = 0
        self.frame = 1
        self.frame_number = 32

        Clock.schedule_once(lambda x: self.update())

    def start(self, frame_number=32, duration=1):
        self.frame_number = frame_number
        self.remaining_time = duration

        if self.complete:
            self.complete = False

            self.anim_event = Clock.schedule_interval(self.next_frame,
                                                      duration / frame_number)

    def pause(self):
        if not self.complete:
            self.anim_event.cancel()

    def resume(self):
        self.anim_event = Clock.schedule_interval(
            self.next_frame, self.remaining_time / frame_number)

    def stop(self):
        self.pause()
        self.reset()

    def reset(self):
        self.complete = True
        self.frame = 1
        self.remaining_time = 0
        self.update()

    def update(self):
        self.source = self.prefix + " ({}).png".format(self.frame)
        self.reload()

    def next_frame(self, dt):
        self.frame += 1
        self.remaining_time -= dt
        self.update()

        if self.frame == self.frame_number:
            self.reset()
            return self.loop


class IrisLogo(AnimatedImage):
    """High level implementation of the animated Iris logo assuming the implicit directory structure is respected"""

    directory = "Iris/resources/iris_animation/"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blink()

    def blink(self):
        self.prefix = self.directory + "iris_blink/iris_blink"
        self.start(frame_number=32, duration=0.5)


class Index(BoxLayout):
    pass


class Link(FloatLayout):
    begin = ObjectProperty()
    end = ObjectProperty()

    color = ColorProperty((0.0, 0.0, 0.0, 1))
    arrow_length = NumericProperty(dp(16))
    arrow_angle = NumericProperty(40)
    line_width = NumericProperty(1.5)
    bezier_distance = NumericProperty(200)
    margin = NumericProperty(dp(6))

    orientation_x = NumericProperty(1)
    orientation_y = NumericProperty(0)

    begin_margin = NumericProperty(dp(32))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.setup)

    def setup(self, *args):
        self.begin.bind(pos=self.draw_link, size=self.draw_link)
        self.end.bind(pos=self.draw_link, size=self.draw_link)
        self.draw_link()

    def _rotate(self, alpha, x, y, cx, cy):
        return (x - cx) * np.cos(alpha) - (y - cy) * np.sin(alpha) + cx, (
            x - cx) * np.sin(alpha) + (y - cy) * np.cos(alpha) + cy

    def get_index(self):
        return self.ids.index.index

    def set_index(self, index):
        self.ids.index.index = index

    def draw_link(self, *args):
        self.canvas.before.clear()

        x1, y1 = self.begin.pos
        x2, y2 = self.end.pos

        w1, h1 = self.begin.size
        w2, h2 = self.end.size

        # Compute best orientation
        if y2 > y1 + h1:
            self.orientation_x = 0
            self.orientation_y = 1
        elif y2 + h2 < y1:
            self.orientation_x = 0
            self.orientation_y = -1
        else:
            if x2 > x1 + h1:
                self.orientation_x = 1
            else:
                self.orientation_x = -1

            self.orientation_y = 0

        # Get center coords of the corresponding side
        if self.orientation_x == 1:
            x1 = x1 + w1
        elif self.orientation_x == 0:
            x1 = x1 + w1 / 2
            x2 = x2 + w2 / 2
        elif self.orientation_x == -1:
            x2 = x2 + w2

        if self.orientation_y == 1:
            y1 = y1 + h1
        elif self.orientation_y == 0:
            y1 = y1 + h1 / 2
            y2 = y2 + h2 / 2
        elif self.orientation_y == -1:
            y2 = y2 + h2

        # Adpat bezier_distance to widget's distance
        if self.orientation_x != 0:
            self.bezier_distance = abs(x1 - x2) / 4
        else:
            self.bezier_distance = abs(y1 - y2) / 4

        x1 = x1 - abs(self.orientation_y) * (
            (self.begin.max_output + 1 - 2 * int(self.get_index())) /
            2) * (self.ids.index.width + 4 * self.margin)
        y1 = y1 + abs(self.orientation_x) * (
            (self.begin.max_output + 1 - 2 * int(self.get_index())) /
            2) * (self.ids.index.height + 4 * self.margin)
        # Index
        self.ids.index.center = (x1 + self.orientation_x *
                                 (self.margin + self.ids.index.width / 2),
                                 y1 + self.orientation_y *
                                 (self.margin + self.ids.index.height / 2))

        x1, y1 = (x1 + self.orientation_x *
                  (2 * self.margin + self.ids.index.width),
                  y1 + self.orientation_y *
                  (2 * self.margin + self.ids.index.height))
        x_mid, y_mid = (x1 + x2) / 2, (y1 + y2) / 2

        # Rotation angle to almost align arrow with line
        alpha = np.arctan2(y1 - y2, x1 - x2)
        x_arrow = x_mid + self.arrow_length * np.cos(
            self.arrow_angle * np.pi / 180)
        y_arrow = y_mid + self.arrow_length * np.sin(
            self.arrow_angle * np.pi / 180)

        self.canvas.before.add(Color(*self.color))
        # Link
        self.canvas.before.add(
            Line(width=self.line_width,
                 bezier=(x1, y1,
                         x1 + self.bezier_distance * self.orientation_x,
                         y1 + self.bezier_distance * self.orientation_y,
                         x2 - self.bezier_distance * self.orientation_x, y2 -
                         self.bezier_distance * self.orientation_y, x2, y2)))
        # Arrow
        self.canvas.before.add(
            Line(width=self.line_width,
                 points=[
                     *self._rotate(alpha, x_arrow, y_arrow, x_mid, y_mid),
                     x_mid, y_mid, *self._rotate(
                         alpha, x_arrow, 2 * y_mid - y_arrow, x_mid, y_mid)
                 ],
                 joint="miter",
                 cap="square"))
        self.canvas.before.add(
            Line(width=self.line_width,
                 points=[
                     x1 + self.orientation_y *
                     (self.ids.index.width / 2 + self.margin),
                     y1 + self.orientation_x *
                     (self.ids.index.height / 2 + self.margin),
                     x1 - self.orientation_y *
                     (self.ids.index.width / 2 + self.margin),
                     y1 - self.orientation_x *
                     (self.ids.index.height / 2 + self.margin)
                 ],
                 cap="square"))


class TaskListItem(OneLineAvatarIconListItem, RectangularRippleBehavior):
    pass


class RightIconButton(IRightBodyTouch, MDIconButton):
    pass


class RightBottomFloatingButton(MDFloatingActionButton):
    margin = NumericProperty(sp(12))


class ScrollingGridLayout(ScrollView):
    def add_widget(self, widget, index=0):
        if isinstance(widget, MDGridLayout):
            super().add_widget(widget)
        else:
            self.scroll_lay.add_widget(widget, index)

    def remove_widget(self, widget):
        self.scroll_lay.remove_widget(widget)


class ChoiceDialog(MDDialog):
    def __init__(self, **kwargs):
        app = MDApp.get_running_app()

        self.validation_btn = MDRaisedButton(
            text="OK", text_color=app.theme_cls.primary_color)
        self.cancel_btn = MDRaisedButton(
            text="CANCEL", text_color=app.theme_cls.primary_color)
        self.callback = kwargs.pop('callback')
        super().__init__(buttons=[self.cancel_btn, self.validation_btn],
                         **kwargs)

        self.validation_btn.bind(on_release=self.update_item)
        self.cancel_btn.bind(on_release=lambda x: self.dismiss())
        self.auto_dismiss = False

    def update_item(self, *args):

        for item in self.items:
            if item.ids.check.active:
                if self.callback:
                    self.callback(self, item.text)
                break
        self.dismiss()


class SelectMenu(ButtonBehavior, RectangularRippleBehavior, BoxLayout):
    items = ListProperty()
    item = ObjectProperty()
    default = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog = None

        self.setup()
        self.bind(on_release=lambda x: self.dialog.open())

    def setup(self, *args):
        if not self.dialog:
            self.dialog = ChoiceDialog(
                title="Operation",
                items=[ItemCheck(**item) for item in self.items],
                type="confirmation",
                callback=lambda i, v: self.set_item(v))

            if self.default != {}:
                self.set_item(self.default["text"])

    def set_item(self, text):
        self.item.text = text


class CheckboxLeftWidget(MDCheckbox, ILeftBodyTouch):
    pass


class ItemCheck(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance_check):
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            check.active = False

        instance_check.active = True


class EnumeratedItem(BoxLayout):
    index = StringProperty("1")

    def get_item(self):
        return self.children[0]


class EnumeratedList(BoxLayout):
    with_add_button = BooleanProperty()
    spacing = NumericProperty(dp(6))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.list = MDList()
        self.list.spacing = self.spacing
        super().add_widget(self.list)

        if self.with_add_button:
            self.add_btn = MDIconButton(icon="plus-circle-outline",
                                        pos_hint={
                                            "center_x": 0.5,
                                            "center_y": 0.5
                                        })
            super().add_widget(self.add_btn)
            self.add_btn.bind(on_release=self.add_item)

            self.register_event_type("on_pre_add_item")
            self.register_event_type("on_pre_remove_item")

    def add_widget(self, widget, index=0, canvas=None):
        self.dispatch("on_pre_add_item", widget.get_item())
        self.list.add_widget(widget, index=index, canvas=canvas)
        self.update_indicies(widget)

    def remove_widget(self, widget):
        self.dispatch("on_pre_remove_item", widget.get_item())
        self.list.remove_widget(widget)
        self.update_indicies(widget)

    def add_item(self, *args):
        copy = EnumeratedItem()
        for child in self.list.children[0].children[0:-1]:
            copy.add_widget(child.__class__())
        self.add_widget(copy)

    def update_indicies(self, instance):
        for i, child in enumerate(self.list.children):
            self.list.children[i].index = str(len(self.list.children) - i)

    def on_pre_add_item(self, *args):
        pass

    def on_pre_remove_item(self, *args):
        pass