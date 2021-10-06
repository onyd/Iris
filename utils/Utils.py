import os
import importlib.util
import sys, inspect
from pathlib import Path
import glob
import re


class Utils:
    @staticmethod
    def convert_path_to_importable(path):
        path = re.sub(r"\\\\|/|//|\\", ".", path)
        path = re.sub(r".py", "", path)
        return path

    # @staticmethod
    # def get_module_name_by_path(path):
    #     for key, value in sys.modules.items():
    #         try:
    #             if Path(value.__file__).resolve() == Path(path).resolve():
    #                 return key
    #         except:
    #             continue

    # # Modules
    # @staticmethod
    # def load_module_by_path(path):
    #     name = Utils.convert_path_to_importable(path)
    #     spec = importlib.util.spec_from_file_location(name, Path(path))
    #     module = importlib.util.module_from_spec(spec)
    #     if sys.modules.get(name, None) is None:
    #         sys.modules[name] = module
    #     spec.loader.exec_module(module)

    #     return module

    # Classes
    @staticmethod
    def get_class_by_name(import_name):
        parts = import_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    # @staticmethod
    # def get_classes_by_path(file_path):
    #     if file_path.endswith(".py"):
    #         module = Utils.load_module_by_path(file_path)
    #         return inspect.getmembers(
    #             sys.modules[Utils.get_module_name_by_path(file_path)],
    #             inspect.isclass)

    # @staticmethod
    # def get_classes_from_dir(path, keep_subclass_of=None):
    #     dir_path = Path(path)
    #     dir_classes = []
    #     for file_name in os.listdir(dir_path):
    #         classes = Utils.get_classes_by_path(str(dir_path / file_name))
    #         if classes:
    #             for cl in classes:
    #                 if cl[1] not in dir_classes:
    #                     if keep_subclass_of is None:
    #                         dir_classes.append(cl[1])
    #                     elif issubclass(cl[1], keep_subclass_of):
    #                         dir_classes.append(cl[1])

    #     return dir_classes
