from Iris.core.Models.Components.Component import Component


class Variable(Component):
    def __init__(self, placeholder, name="", value=0, settings=None, **kwargs):
        super().__init__(settings=settings, **kwargs)
        self.placeholder = placeholder
        self.name = name
        self.value = value

    def __call__(self, buffer, **kwargs):
        buffer.update({self.name: self.value})

    def to_dict(self, **kwargs):
        return super().to_dict(placeholder=self.placeholder,
                               name=self.name,
                               value=self.value,
                               **kwargs)
