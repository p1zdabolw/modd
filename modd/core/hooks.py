import pluggy

hookspec = pluggy.HookspecMarker("modd")


class HookSpecs:
    @hookspec
    def get_adapter(self):
        raise NotImplementedError
