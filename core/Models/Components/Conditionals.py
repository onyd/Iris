from functools import partial

from Iris.GUI.Widgets import StackLayout, SelectMenu, EnumeratedItem, NumericProperty, ObjectProperty, dp
from Iris.core.Models.Components.Component import Component, SerializableObject, ExecutableObject, BoxLayout, StringProperty
from Iris.core.Models.Components.Variables import *
from Iris.utils.Structures.Lifo import Lifo


class Condition(BoxLayout, SerializableObject, ExecutableObject):
    # TODO SelectMenu not diplayed correctly because now not scheduled
    left_value_input = ObjectProperty()
    operator_menu = ObjectProperty()
    right_value_input = ObjectProperty()

    def __init__(self,
                 left_value="",
                 operator="=",
                 right_value="",
                 settings=None,
                 **kwargs):
        super().__init__(**kwargs)

        self.left_value = left_value
        self.operator = operator
        self.right_value = right_value

    def setup_gui(self, *args):
        self.left_value_input.bind(
            text=lambda instance, text: setattr(self, 'left_value', text))
        self.operator_menu.item.bind(
            text=lambda instance, text: setattr(self, 'operator', text))
        self.right_value_input.bind(
            text=lambda instance, text: setattr(self, 'right_value', text))

        self.left_value_input.text = self.left_value
        self.operator_menu.item.text = self.operator
        self.right_value_input.text = self.right_value

    def __call__(self, buffer, **kwargs):

        if self.operator == ">":
            return self.left_val > self.right_val
        elif self.operator == ">=":
            return self.left_val >= self.right_val
        elif self.operator == "<":
            return self.left_val < self.right_val
        elif self.operator == "<=":
            return self.left_val <= self.right_val
        elif self.operator == "==":
            return self.left_val == self.right_val
        elif self.operator == "!=":
            return self.left_val != self.right_val
        elif self.operator == "in":
            return self.left_val in self.right_val
        elif self.operator == "&":
            return self.left_val & self.right_val
        elif self.operator == "|":
            return self.left_val | self.right_val

    def to_dict(self, **kwargs):
        return super().to_dict(left_value=self.left_value,
                               operator=self.operator,
                               right_value=self.right_value,
                               **kwargs)


class ConditionStack(StackLayout, SerializableObject, ExecutableObject):
    spacing_x = NumericProperty(dp(6))
    add_btn = ObjectProperty()

    def __init__(self, conditions=None, junctions=[], settings=None, **kwargs):
        super().__init__(**kwargs)
        self.conditions = conditions if conditions else [
            Condition(size_hint_x=None)
        ]
        self.junctions = junctions

    def setup_gui(self, *args):
        self.remove_widget(self.add_btn)
        self.conditions[0].size_hint_x = None
        self.add_widget(self.conditions[0])
        for i in range(1, len(self.conditions)):
            menu = SelectMenu(items=[{
                "text": "and"
            }, {
                "text": "or"
            }],
                              default={"text": self.junctions[i - 1]})
            self.conditions[i].size_hint_x = None

            self.add_widget(menu)
            self.add_widget(self.conditions[i])
            menu.bind(size=self.update_condition_width)
            menu.item.bind(text=partial(self.update_junction, i - 1))

        self.add_widget(self.add_btn)
        self.bind(size=self.update_condition_width)
        self.update_condition_width()

    def __call__(self, buffer, **kwargs):
        result = self.conditions[0](buffer)
        for i in range(1, len(self.conditions)):
            if self.junctions[i - 1] == "and":
                result &= self.conditions[i](buffer)
            else:
                result |= self.conditions[i](buffer)

        return result

    def add_condition(self, *args):
        menu = SelectMenu(items=[{"text": "and"}, {"text": "or"}])
        condition = Condition(size_hint_x=None)

        self.remove_widget(self.add_btn)
        self.add_widget(menu)
        self.add_widget(condition)
        self.add_widget(self.add_btn)

        menu.bind(size=self.update_condition_width)
        self.update_condition_width()

        self.conditions.append(condition)
        self.junctions.append(menu.item.text)

    def update_condition_width(self, *args):
        conditions = Lifo()
        children = Lifo(self.children)
        non_conditions_width = 0

        n = 0
        while not children.empty():
            widget = children.pop()
            n += 1
            if isinstance(widget, Condition):
                conditions.push(widget)
            else:
                non_conditions_width += widget.width

            # There is 2 conditions, make the two fit one line
            if n == 4:
                n = 0
                while not conditions.empty():
                    conditions.pop().width = (self.width - non_conditions_width
                                              ) / 2 - 2 * self.spacing_x
                non_conditions_width = 0
        # Last line is incomplete, make it larger
        if not conditions.empty():
            conditions.pop(
            ).width = self.width - self.add_btn.width - self.spacing_x

    def update_junction(self, index, instance, value):
        self.junctions[index] = value

    def to_dict(self, **kwargs):
        return super().to_dict(conditions=self.conditions,
                               junctions=self.junctions,
                               **kwargs)


class Cases(Component):
    icon = StringProperty("animation-play.png")

    def __init__(self, value, cases, settings=None, **kwargs):
        super().__init__(settings=settings, **kwargs)

    def __call__(self, buffer, **kwargs):
        pass


class If(Component):
    def __init__(self, condition_stacks=None, settings=None, **kwargs):
        super().__init__(settings=settings, **kwargs)
        self.condition_stacks = condition_stacks if condition_stacks else [
            ConditionStack()
        ]

        self.max_output = 2

    def setup_gui(self, *args):
        for condition_stack in self.condition_stacks:
            item = EnumeratedItem()
            item.add_widget(condition_stack)
            self.ids.condition_stack_list.add_widget(item)

        self.max_output = len(self.condition_stacks) + 1
        self.ids.condition_stack_list.bind(
            on_pre_add_item=self.add_condition_stack)
        self.ids.condition_stack_list.bind(
            on_pre_remove_item=self.remove_condition_stack)

    def add_condition_stack(self, instance, widget):
        self.condition_stacks.append(widget)
        self.max_output += 1

    def remove_condition_stack(self, instance, widget):
        self.condition_stacks.remove(widget)
        self.max_output -= 1

    def __call__(self, buffer, **kwargs):
        for i, condition_stack in enumerate(self.condition_stacks):
            if condition_stack(buffer, **kwargs):
                return i

        return len(
            self.condition_stacks
        ) + 1  # Means no condition_stack has been true so continue with last output: the else output

    def to_dict(self, **kwargs):
        return super().to_dict(condition_stacks=self.condition_stacks,
                               **kwargs)


class While(Component):
    icon = StringProperty("autorenew.png")

    def __init__(self, settings=None, **kwargs):
        super().__init__(settings=settings, **kwargs)

    def __call__(self, buffer, **kwargs):
        pass


class For(Component):
    icon = StringProperty("refresh.png")

    def __init__(self, iterations=0, settings=None, **kwargs):
        super().__init__(settings=settings, **kwargs)
        self.iterations = iterations

    def __call__(self, buffer, **kwargs):
        pass
