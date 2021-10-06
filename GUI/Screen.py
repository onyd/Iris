from pathlib import Path
import os
from functools import partial

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from kivy.properties import ListProperty, ObjectProperty, ColorProperty

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import Scatter, ScatterLayout

from kivymd.app import MDApp
from kivymd.uix.toolbar import MDToolbar, MDBottomAppBar
from kivymd.uix.button import MDFlatButton
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField

from Iris.core.Models.Components.Component import Component
from Iris.core.Models.Components.Actions import *
from Iris.core.Models.Components.Conditionals import *
from Iris.core.Models.Components.Variables import *
from Iris.GUI.Widgets import *
from Iris.core.Models.Tasks.TaskManager import TaskManager, TaggedGraph
from Iris.utils.Utils import Utils


class HomeScreen(Screen):
    pass


class ConversationsScreen(Screen):
    pass


class DashboardScreen(Screen):
    pass


class ChooseEditorScreen(Screen):
    pass


class TaskEditorScreen(Screen):

    right_action_items = ListProperty([])
    left_action_items = ListProperty([])

    def __init__(self, **kw):
        self.task_manager = TaskManager()
        self.pre_selected = None

        self.register_event_type("on_edit_mode")
        self.register_event_type("on_selection_mode")

        self.app = MDApp.get_running_app()

        super().__init__(**kw)

    def hide_action_bar(self):
        """Hide the bottom action bar"""
        self.remove_widget(self.bottom_action_bar)

    def show_action_bar(self):
        """Show the bottom action bar"""
        self.add_widget(self.bottom_action_bar)

    # Menus
    def open_task_list(self):
        """Open a scrollable list of available tasks and setup a button to create new task in the editor"""
        scrollable_task = ScrollView()
        scrollable_task.add_widget(self.get_task_list())

        new_task_btn = RightBottomFloatingButton(
            icon='plus',
            md_bg_color=self.app.theme_cls.accent_color,
            elevation_normal=8)
        new_task_btn.bind(on_press=lambda x: self.open_create_task_dialog())

        self.task_list_layout.add_widget(scrollable_task)
        self.task_list_layout.add_widget(new_task_btn)

        self.task_list.open()

    def open_create_task_dialog(self):
        """Called when a new task is being created, it ask the name of the task and save/open it with just the StartComponent"""
        color = self.app.theme_cls.primary_color

        create_btn = MDFlatButton(text="OK", text_color=color)
        cancel_btn = MDFlatButton(text="CANCEL", text_color=color)
        name_field = MDTextField(hint_text="Name")

        dialog = MDDialog(title="Create a new Task",
                          type="custom",
                          content_cls=name_field,
                          buttons=[cancel_btn, create_btn])
        dialog.auto_dismiss = False

        def create_task(*args):
            self.task_list.dismiss()
            dialog.dismiss()

            self.task_manager.save(name_field.text)

        create_btn.bind(on_press=create_task)
        cancel_btn.bind(on_press=lambda x: dialog.dismiss())

        dialog.open()

    def open_edit_task_dialog(self):
        pass

    def open_component_menu(self):
        """Open SheetView with 4 tabs, which regroup type of component
        Click on an associated component button start place_component_mode with it"""
        sheet_menu = SheetView(size_hint=(1, 0.8), radius=[
            15,
        ])
        tabs = ComponentMenuSheet()
        sheet_menu.add_widget(tabs)
        component_dict = {
            "actions": [Print],
            "conditionals": [If, Cases, While, For],
            "variables": [Variable]
        }

        def setup_place_mode(component_cls, *args):
            component = component_cls()
            self.add_component(
                component, *self.ids.edit_area.to_local(*self.ids.view.center))
            self.place_mode_component(component)
            sheet_menu.dismiss()

        # Sort them by type
        for section, component_classes in component_dict.items():
            for component_class in component_classes:
                component_btn = RectangleIconLabelButton(
                    text=component_class.__name__,
                    source=res_dir + "/" + component_class.icon.defaultvalue,
                    size_hint=(1, None))
                component_btn.ids.icon.size_hint = 1, None
                component_btn.frame_color = self.app.theme_cls.accent_color
                component_btn.md_bg_color = self.app.theme_cls.bg_light

                tabs.ids[section + "_lay"].add_widget(component_btn)

                component_btn.bind(
                    minimum_height=component_btn.setter('height'))
                component_btn.bind(
                    on_press=partial(setup_place_mode, component_class))

        sheet_menu.open()

    def get_task_list(self):
        """Load the available tasks:
        return the MDList with all available tasks as ListItem"""
        tasks = MDList()

        settings = self.app.settings
        path = Path(settings.paths.get('task_path'))
        for file_name in os.listdir(path):
            if file_name.endswith('.json'):
                task = TaskListItem(text=file_name[:-5])
                task.bind(on_release=self.open_task)
                tasks.add_widget(task)

        return tasks

    def open_task(self, instance):
        """Close the task list view and show the editor with selected task"""
        self.task_manager.load(instance.text)

        # Build the task in editor
        for component in self.task_manager.task.graph.V:
            self.add_component(component)
            for tagged_link in self.task_manager.task.graph[component]:
                self.task_manager.add_editor_link(
                    component,
                    self.task_manager.task.graph.V[tagged_link.vertex_index],
                    self.ids.edit_area,
                    index=tagged_link.tag)
        self.task_list.dismiss()

    # Component/TaggedGraph operations
    def add_component(self, component, x=None, y=None):
        """Add a component:
            component: the component to add
            x: the x coordinate of the component
            y: the y coordinate of the component"""
        self.ids.edit_area.add_widget(component)
        if x and y:
            component.pos = x, y
        self.task_manager.task.graph.add_vertex(component)

        component.bind(on_add_link=self.add_link,
                       on_remove_link=self.remove_link)
        self.bind(on_edit_mode=component.edit_mode,
                  on_selection_mode=component.selection_mode)

    def remove_component(self, component):
        """Remove a component:
            component: the component to remove
            """
        self.task_manager.task.graph.remove_vertex(component)
        self.ids.edit_area.remove_widget(component)

    def place_mode_component(self, component):
        """Enter in place component mode (not a mode as link mode):
            component: the component to place, which will be centered in the view, touch transparent, and an add button to place it
            """
        def center_component(*args):
            component.center = self.ids.edit_area.to_local(
                *self.ids.view.center)

        self.ids.edit_area.bind(on_transform_with_touch=center_component)

        # Validation
        validation_btn = RightBottomFloatingButton(
            icon='check',
            md_bg_color=self.app.theme_cls.accent_color,
            elevation_normal=8)
        self.add_widget(validation_btn)

        def validate_pos(*args):
            self.change_mode(None)
            self.remove_widget(validation_btn)
            self.ids.edit_area.unbind(on_transform_with_touch=center_component)

        validation_btn.bind(on_press=validate_pos)

        def reset_mode(*args):
            self.remove_component(component)
            self.remove_widget(validation_btn)
            self.change_mode(None)

        self.app.set_disabled_tool_bar(reset_mode)
        self.hide_action_bar()
        component.sdb_enabled = False

    def delete_mode_component(self, component=None):
        """Enter in delete mode:
            component: the component to remove, first call with component=None will look for selected component and ignite a second call which will delete it"""
        if component:
            # Remove all links with its neighbors
            for neighbor in self.task_manager.task.graph.unoriented_neighbors(
                    component):
                self.task_manager.remove_editor_link(component, neighbor,
                                                     self.ids.edit_area)

            self.remove_component(component)

        else:
            for child in self.ids.edit_area.content.children:
                if isinstance(child, Component) and child.selected:
                    self.delete_mode_component(child)
                    break

            print("Error: no selected component")

    def add_link(self, _, instance):
        """Called when mode="add_link" and a component is clicked, add link if two components have been selected else register selection and wait for second call:
            instance: the component object that has been clicked """
        # Take the first selection
        if self.pre_selected is None:
            self.pre_selected = instance
            instance.select()
        elif self.pre_selected != instance:
            # The selection is correct and no link exist in both direction
            if not self.task_manager.task.graph.adjacent(
                    self.pre_selected,
                    instance) and not self.task_manager.task.graph.adjacent(
                        instance, self.pre_selected):
                self.task_manager.add_editor_link(self.pre_selected, instance,
                                                  self.ids.edit_area)
                self.change_mode(None)
            else:
                print("Error: link already exist")
                self.change_mode(None)
        else:
            self.pre_selected.unselect()
            self.pre_selected = None

    def remove_link(self, _, instance):
        """Called when mode="remove_link" and a component is clicked, remove link if two components have been selected else register selection and wait for second call:
            instance: the component object that has been clicked """
        # Take the first selection
        if self.pre_selected is None:
            self.pre_selected = instance
            instance.select()
        # The selection is correct
        elif self.pre_selected != instance:
            # Remove the link whatever the order of selection
            if self.task_manager.task.graph.adjacent(self.pre_selected,
                                                     instance):
                self.task_manager.remove_editor_link(self.pre_selected,
                                                     instance,
                                                     self.ids.edit_area)
                self.change_mode(None)
            elif self.task_manager.task.graph.adjacent(instance,
                                                       self.pre_selected):
                self.task_manager.remove_editor_link(instance,
                                                     self.pre_selected,
                                                     self.ids.edit_area)
                self.change_mode(None)
            else:
                print("Error: no link")
                self.change_mode(None)
        else:
            self.pre_selected.unselect()
            self.pre_selected = None

    # Misc
    def change_mode(self, mode=None):
        """Change the mode, edit mode for default behavior like drag, select one component ... and selection mode for enable selection of two components, with drag disabled, bottom bar hidden:
            mode: the mode (None=default, 'add_link', 'remove_link' """
        if mode is None:
            self.dispatch("on_edit_mode", mode)
        else:
            self.dispatch("on_selection_mode", mode)

        print(f"->Change link mode to {mode} mode")

    def to_center(self):
        """Go to the center of the edit_area"""
        self.ids.edit_area.to_center()

    # Event
    def on_edit_mode(self, mode):
        """Setup the bars properties for edit mode"""
        self.pre_selected = None

        self.app.tool_bar.md_bg_color = self.app.theme_cls.primary_color
        self.app.set_lab_tool_bar()
        self.show_action_bar()

    def on_selection_mode(self, mode):
        """Setup the bars properties for selection mode"""
        self.app.tool_bar.md_bg_color = self.app.theme_cls.accent_color
        self.app.set_disabled_tool_bar(lambda: self.change_mode(None))
        self.hide_action_bar()

    def on_leave(self, *args):
        """Un load edit_area contents"""
        self.ids.edit_area.content.clear_widgets()
        return super().on_leave(*args)

    def on_pre_enter(self):
        """Initialize some widgets and display task list"""

        # Setup task list
        self.task_list = SheetView()
        self.task_list_layout = FloatLayout()
        self.task_list.add_widget(self.task_list_layout)

        # Tool bar
        self.ids.action_bar.on_action_button = lambda: self.open_component_menu(
        )

        self.open_task_list()

        self.app.tool_bar.right_action_items.append(
            ['image-filter-center-focus', lambda x: self.to_center()])


class ReflexEditorScreen(Screen):
    pass


class SceneEditorScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass
