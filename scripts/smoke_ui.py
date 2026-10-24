import os
import sys
import tempfile
import time

from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from modd.core.plugin_manager import create_manager
from modd.core.registry import GameRegistry
from modd.plugins import stalker_xray, unreal, unity, witcher_red
from modd.ui.i18n import I18n
from modd.ui.icon import build_app_icon, save_ico
from modd.ui.main_window import MainWindow
from modd.ui.theme import STYLESHEET

app = QApplication([])
app.setStyleSheet(STYLESHEET)
manager = create_manager()
for plugin in (stalker_xray, witcher_red, unreal, unity):
    manager.register(plugin)
registry = GameRegistry(manager)
i18n = I18n()
window = MainWindow(registry, i18n)
window.show()
app.processEvents()

project = Path(tempfile.mkdtemp()) / "demo"
(project / "mods").mkdir(parents=True)
(project / "mods" / "main.py").write_text("value = 2\nprint('marker', value)\n", encoding="utf-8")
(project / "mod.toml").write_text('name = "demo"\ngame = "unity"\n', encoding="utf-8")
window._attach_project(str(project))
app.processEvents()
editor = window.open_file(project / "mods" / "main.py")
app.processEvents()
window._run_current()
deadline = time.time() + 15
while time.time() < deadline:
    app.processEvents()
    if window._session is None:
        break
    time.sleep(0.05)

i18n.set_language("ru")
app.processEvents()
window.retranslate()
app.processEvents()

assets = Path(__file__).resolve().parent.parent / "assets"
assets.mkdir(exist_ok=True)
save_ico(str(assets / "modd.ico"))
ico_bytes = (assets / "modd.ico").read_bytes()
icon = build_app_icon()

checks = {
    "adapters": len(registry.adapters()) == 4,
    "adapter_detected": window._adapter is not None and window._adapter.game_id == "unity",
    "tab_opened": window._tabs.count() == 1,
    "session_finished": window._session is None,
    "console_output": "marker 2" in window._console._view.toPlainText(),
    "russian_title": window.windowTitle() == i18n.tr("window.title"),
    "ico_header": ico_bytes[:4] == b"\x00\x00\x01\x00" and ico_bytes[4:6] == b"\x06\x00",
    "icon_sizes": icon.availableSizes()[0].width() > 0,
}
for name, passed in checks.items():
    print("CHECK", name, "OK" if passed else "FAIL")
print("RESULT", "OK" if all(checks.values()) else "FAIL")
sys.exit(0 if all(checks.values()) else 1)
