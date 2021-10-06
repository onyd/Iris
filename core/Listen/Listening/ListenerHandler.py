from Iris.utils.Logging.ConsolePrinter import ConsolePrinter
from Iris.core.Listen.Matching.Matcher import Matcher
from Iris.core.Execution.TaskRunner import TaskRunner


class ListenerHandler:
    def __init__(self, settings=None):
        self.matcher = Matcher(settings)
        self.task_runner = TaskRunner(settings=settings)
        self.settings = settings

    def trigger(self, signal):
        # First we check if a signal correspond to an existing reflex
        matched = self.matcher.match_by_signal(signal)
        if matched and matched[0].enabled:
            ConsolePrinter.print_debug("Trigger has been called")
            # Call task runner to create a new buffer and execute tasks
            reflex, buffer = matched
            self.task_runner.push_reflex(reflex, buffer)
            self.task_runner.execute()
