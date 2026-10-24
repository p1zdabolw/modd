import sys

from PySide6.QtWidgets import QApplication

from modd.core.plugin_manager import create_manager
from modd.core.registry import GameRegistry
from modd.plugins import stalker_xray, unreal, unity, witcher_red
from modd.ui.i18n import I18n
from modd.ui.icon import build_app_icon
from modd.ui.main_window import MainWindow
from modd.ui.theme import STYLESHEET

BUILTIN_PLUGINS = (stalker_xray, witcher_red, unreal, unity)


def main():
    manager = create_manager()
    for plugin in BUILTIN_PLUGINS:
        manager.register(plugin)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Modd")
    app.setOrganizationName("modd")
    app.setStyleSheet(STYLESHEET)
    app.setWindowIcon(build_app_icon())
    i18n = I18n(app)
    registry = GameRegistry(manager)
    window = MainWindow(registry, i18n)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
