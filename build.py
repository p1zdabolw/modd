import os
import subprocess
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtGui import QGuiApplication

    from modd.ui.icon import save_ico

    app = QGuiApplication([])
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    save_ico(str(assets / "modd.ico"))
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "modd.spec", "--noconfirm"],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
