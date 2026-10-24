from pathlib import Path

from modd.core.game_adapter import GameAdapter, ModPackage
from modd.core.plugin_manager import hookimpl


class WitcherRedAdapter(GameAdapter):
    game_id = "witcher_red"
    title = "The Witcher 3 (RED engine)"

    def detect(self, path: Path) -> bool:
        return (path / "bin" / "x64" / "witcher3.exe").is_file() or (path / "mods").is_dir()

    def validate(self, package: ModPackage) -> list:
        return self.check_python_entry(package)

    def build(self, package: ModPackage) -> Path:
        raise NotImplementedError

    def deploy(self, package: ModPackage) -> Path:
        raise NotImplementedError


@hookimpl
def get_adapter():
    return WitcherRedAdapter()
