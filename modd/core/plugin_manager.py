import pluggy

from modd.core.hooks import HookSpecs

hookimpl = pluggy.HookimplMarker("modd")


def create_manager():
    manager = pluggy.PluginManager("modd")
    manager.add_hookspecs(HookSpecs)
    return manager
