from kivy.properties import StringProperty

from Iris.core.Models.Components.Component import Component
from Iris.utils.Logging.ConsolePrinter import ConsolePrinter


class Print(Component):
    icon = StringProperty("lead-pencil.png")
    text = StringProperty()
    value = StringProperty()

    def __init__(self, value="", settings=None, **kwargs):
        super().__init__(settings=settings, **kwargs)

    def setup_gui(self, *args):
        super().setup_gui(*args)

    def __call__(self, buffer, **kwargs):
        ConsolePrinter.print_result(self.value)

    def to_dict(self, **kwargs):
        return super().to_dict(value=self.value, **kwargs)
