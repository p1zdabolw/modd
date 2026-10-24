from pathlib import Path

from modd.core.game_adapter import GameAdapter, ModPackage
from modd.core.plugin_manager import hookimpl


class UnityAdapter(GameAdapter):
    game_id = "unity"
    title = "Unity"

    def detect(self, path: Path) -> bool:
        return (path / "Assets").is_dir() and (path / "ProjectSettings").is_dir()

    def validate(self, package: ModPackage) -> list:
        return self.check_python_entry(package)

    def build(self, package: ModPackage) -> Path:
        raise NotImplementedError

    def deploy(self, package: ModPackage) -> Path:
        raise NotImplementedError


@hookimpl
def get_adapter():
    return UnityAdapter()
