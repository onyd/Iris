from Iris.core.Models.Components.Component import Component
from Iris.utils.Utils import Utils

directory = "Iris/core/Models/Components/"

print(Utils.get_classes_from_dir(directory, Component))