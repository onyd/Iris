from os import name
from pathlib import Path

from Iris.core.Models.Components.Component import SerializableObject
from Iris.utils.Structures.TaggedGraph import TaggedGraph
from Iris.utils.FileProcessing.FileManager import FileManager


class Task(SerializableObject):
    """This is the model of a general task where:
            name: allow to caracterize the task (has to be unique)
            graph: the TaggedGraph which represent execution graph"""
    def __init__(self, name, graph, settings=None):
        self.name = name
        self.graph = graph
        self.settings = settings

    def __call__(self, buffer):
        start = self.graph.V[0]

        # Find

    @staticmethod
    def get_task_path_by_name(name, settings):
        """name: the task name
        return: the path to the task file"""
        task_path = Path(settings.paths.get('task_path'))

        return task_path / (name + ".json")

    def to_dict(self):
        super().to_dict(self.graph)

    @classmethod
    def load_task(cls, name, settings):
        """Build the task from data where:
              path: path to json encoded dict containing all necessary data to rebuild components and links (assuming that stored object inherit from SerializableObject)
          return: the corresponding Task object"""
        data = FileManager.load_json(Task.get_task_path_by_name(
            name, settings))

        return cls.from_dict(data, settings, name=name)
