from pathlib import Path
import os

from kivymd.app import MDApp

from Iris.core.Models.Tasks.Task import Task
from Iris.utils.Structures.TaggedGraph import TaggedGraph, TaggedLink
from Iris.GUI.Widgets import Link, ChoiceDialog, ItemCheck
from Iris.core.Models.Components.Component import StartComponent
from Iris.utils.FileProcessing.FileManager import FileManager
from Iris.utils.Utils import Utils


class TaskManager:
    def __init__(self, settings=None):
        self.task = None
        self.settings = MDApp.get_running_app().settings
        self.links = []

    def get_output_number(self, component):
        return len(self.task.graph[component])

    def add_editor_link(self, begin, end, link_container, index=None):
        """Add an oriented link (graph + graphics) :
            begin: the first component
            end: the second component
            link_container: the widget which will be the parent of graphic link
            """
        output_number = self.get_output_number(begin)

        def create_link(index):
            self.task.graph.add_link(begin, end, index)

            link = Link(begin=begin, end=end)
            link.set_index(index)
            link_container.add_widget(link)

            self.links.append(link)

        # If index is given the call is from open_task so don't need to check output stuff
        if index:
            create_link(index=index)

        # Too many outputs
        elif output_number >= begin.max_output:
            print("Error: already too many outputs")

        elif begin.max_output - output_number > 1:
            # So the component output is ambiguous
            tags = [tagged_link.tag for tagged_link in self.task.graph[begin]]
            dialog = ChoiceDialog(title="Available outputs :",
                                  type="confirmation",
                                  items=[
                                      ItemCheck(text=f'{i+1}')
                                      for i in range(begin.max_output)
                                      if str(i + 1) not in tags
                                  ],
                                  callback=lambda i, v: create_link(v))
            dialog.open()
        else:
            # Find missing index
            index = 1
            tags = [tagged_link.tag for tagged_link in self.task.graph[begin]]

            while index <= begin.max_output:
                if str(index) in tags:
                    index += 1
                else:
                    break
            create_link(index=str(index))

    def remove_editor_link(self, begin, end, link_container):
        """Remove link in graph and graphics stuff:
            begin: the first component
            end: the second component
            (if the orientation is reversed, it retry with begin and end reversed)"""
        # Delete link in graph
        if self.task.graph.adjacent(begin, end):
            self.task.graph.remove_link(begin, end)
        else:
            try:
                self.task.graph.remove_link(end, begin)
            except:
                print("Error: no link")
                return

        # Find graphic link to delete it
        for link in self.links:
            if (link.begin, link.end) == (begin, end) or (link.begin,
                                                          link.end) == (end,
                                                                        begin):
                link_container.remove_widget(link)
                self.links.remove(link)
                return

    def save(self, name=None):
        """Save the task where:
            name: the name of the task if created (if None, it is the current task)"""

        if self.task is None:
            self.task = Task(name,
                             TaggedGraph([StartComponent("<start>")], [[]]))

        FileManager.save_json(
            Task.get_task_path_by_name(self.task.name, self.settings),
            self.task.to_dict())

    def delete(self, name=None):
        """Delete the current_graph if it has been saved
          return: None"""
        path = Task.get_task_path_by_name(name, self.settings)
        if path:
            FileManager.delete_file(path)
        else:
            pass  # print error message

    def load(self, name):
        """Shortcut to load the task:
            name: the task name to load"""
        self.task = Task.load_task(name, self.settings)
