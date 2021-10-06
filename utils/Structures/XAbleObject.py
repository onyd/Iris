from Iris.utils.Utils import Utils


class SerializableObject:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self, **kwargs):
        # Recursively serialize data object in list
        for key, value in kwargs.items():
            serialized = []
            if isinstance(value, list):
                for x in value:
                    try:
                        serialized.append(x.to_dict())
                    except:
                        serialized.append(x)
                kwargs[key] = serialized

        obj = {
            'module': self.__class__.__module__,
            'class_name': self.__class__.__name__,
        }
        obj.update(kwargs)
        return obj

    @staticmethod
    def from_dict(data, settings, **kwargs):
        module_class_name = ""
        try:
            module_class_name = data['module'] + "." + data['class_name']
            del data['module']
            del data['class_name']
        except:
            return data

        # Recursively deserialize data object in list
        for key, value in data.items():
            if isinstance(value, list):
                deserialized = []
                for x in value:
                    try:
                        deserialized.append(
                            SerializableObject.from_dict(x, settings))
                    except:
                        deserialized.append(x)
                data[key] = deserialized
        object_class = Utils.get_class_by_name(module_class_name)
        data.update(kwargs)
        obj = object_class(**data, settings=settings)
        return obj


class ExecutableObject:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def start_setup_gui(*args):
            if args[1]:
                self.setup_gui(*args)

        self.bind(parent=start_setup_gui)

    def __call__(self, *args, **kwargs):
        pass

    def setup_gui(self, *args):
        pass
