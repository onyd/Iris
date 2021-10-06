import random

from Iris.utils.Structures.Lifo import Lifo
from Iris.utils.Logging.ConsolePrinter import ConsolePrinter


class TaskRunner:
    def __init__(self, buffer={}, settings=None):
        self.exec_lifo = Lifo()
        self.buffer = buffer
        self.settings = settings

        self.busy = False

    def execute(self):
        if self.busy:
            return

        self.busy = True
        while not self.exec_lifo.empty():
            current_task = self.exec_lifo.pop()
            ConsolePrinter.print_debug("The task :" + str(current_task) +
                                       "has been triggered")

            # We call the task with available parameters in cache and get the result
            success, buffer = current_task(self.buffer)
            ConsolePrinter.print_debug("The task : " + str(current_task) +
                                       "has returned : " + str(success))
            if not success:
                # if there are missing param, we launch an QuestionTask to get them
                self.settings.voice_engine.speak(
                    random.choice(self.settings['error_response']))
            else:
                self.buffer.update(buffer)

        self.busy = False

    def push_reflex(self, reflex, buffer):
        self.buffer.update(buffer)

        self.push_tasks(reflex.tasks)

    def push_tasks(self, tasks):
        # Reverse to keep written order
        for i in range(len(tasks) - 1, -1, -1):
            self.exec_lifo.push(tasks[i])
