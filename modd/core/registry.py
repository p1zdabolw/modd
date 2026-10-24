class GameRegistry:
    def __init__(self, manager):
        self._manager = manager
        self._adapters = []
        self.reload()

    def reload(self):
        self._adapters = [adapter for adapter in self._manager.hook.get_adapter() if adapter is not None]

    def adapters(self):
        return list(self._adapters)

    def by_id(self, game_id):
        for adapter in self._adapters:
            if adapter.game_id == game_id:
                return adapter
        return None
