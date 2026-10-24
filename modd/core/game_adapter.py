import ast

from abc import ABC, abstractmethod
from pathlib import Path


class ModPackage:
    def __init__(self, root: Path, name: str, game_id: str):
        self.root = root
        self.name = name
        self.game_id = game_id


class GameAdapter(ABC):
    game_id: str = ""
    title: str = ""

    @abstractmethod
    def detect(self, path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def validate(self, package: ModPackage) -> list:
        raise NotImplementedError

    @abstractmethod
    def build(self, package: ModPackage) -> Path:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, package: ModPackage) -> Path:
        raise NotImplementedError

    def check_python_entry(self, package: ModPackage) -> list:
        entry = package.root / "mods" / "main.py"
        if not entry.is_file():
            return [(str(entry), 0, "entry script mods/main.py is missing")]
        source = entry.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as error:
            return [(str(entry), error.lineno or 0, error.msg)]
        return []
