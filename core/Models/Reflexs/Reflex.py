from Iris.core.Models.Tasks.Task import Task


class Reflex:
    def __init__(self, name, signals, tasks, enabled, settings):
        self.name = name
        self.signals = signals
        self.load_tasks(tasks, settings)
        self.enabled = enabled

        self.settings = settings

    def load_tasks(self, tasks):
        self.tasks = [Task.load_task(name, self.settings) for name in tasks]
