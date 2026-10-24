from pathlib import Path

from modd.core.game_adapter import GameAdapter, ModPackage
from modd.core.plugin_manager import hookimpl


class StalkerXrayAdapter(GameAdapter):
    game_id = "stalker_xray"
    title = "S.T.A.L.K.E.R. (X-Ray engine)"

    def detect(self, path: Path) -> bool:
        return (path / "gamedata").is_dir() or (path / "fsgame.ltx").is_file()

    def validate(self, package: ModPackage) -> list:
        return self.check_python_entry(package)

    def build(self, package: ModPackage) -> Path:
        raise NotImplementedError

    def deploy(self, package: ModPackage) -> Path:
        raise NotImplementedError


@hookimpl
def get_adapter():
    return StalkerXrayAdapter()
