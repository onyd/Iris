from Iris.utils.DataProcessing.DataBuilder import DataBuilder
from Iris.Config.SettingsManager import SettingsManager
from Iris.core.Structures.Reflexs.ReflexsManager import ReflexsManager
settings = SettingsManager()

#reflexs = ReflexsManager.parse_reflexs(settings)
DataBuilder.save_order_datasets_to_reflexs(settings)
