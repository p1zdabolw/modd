from pathlib import Path

from modd.core.game_adapter import GameAdapter, ModPackage
from modd.core.plugin_manager import hookimpl


class UnrealAdapter(GameAdapter):
    game_id = "unreal"
    title = "Unreal Engine 4/5"

    def detect(self, path: Path) -> bool:
        return next(path.glob("*.uproject"), None) is not None

    def validate(self, package: ModPackage) -> list:
        return self.check_python_entry(package)

    def build(self, package: ModPackage) -> Path:
        raise NotImplementedError

    def deploy(self, package: ModPackage) -> Path:
        raise NotImplementedError


@hookimpl
def get_adapter():
    return UnrealAdapter()
