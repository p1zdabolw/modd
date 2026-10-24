import re

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

TEMPLATE = "def apply(ctx):\n    raise NotImplementedError\n"
NAME_PATTERN = re.compile(r"[^\w\- ]+")


class CreateProjectPanel(QWidget):
    project_created = Signal(str)
    back_requested = Signal()
    message = Signal(str)

    def __init__(self, registry, i18n, parent=None):
        super().__init__(parent)
        self._registry = registry
        self._i18n = i18n
        self._dialog = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(10)
        self._title = QLabel()
        self._title.setObjectName("panelTitle")
        layout.addWidget(self._title)
        self._name_label = QLabel()
        self._name = QLineEdit()
        self._game_label = QLabel()
        self._game = QComboBox()
        for adapter in registry.adapters():
            self._game.addItem(adapter.title, adapter.game_id)
        self._folder_label = QLabel()
        self._folder = QLineEdit()
        self._browse = QToolButton()
        self._browse.clicked.connect(self._pick_folder)
        folder_row = QHBoxLayout()
        folder_row.setSpacing(6)
        folder_row.addWidget(self._folder, 1)
        folder_row.addWidget(self._browse)
        form = QFormLayout()
        form.setSpacing(10)
        form.addRow(self._name_label, self._name)
        form.addRow(self._game_label, self._game)
        form.addRow(self._folder_label, folder_row)
        layout.addLayout(form)
        layout.addStretch(1)
        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self._create = QPushButton()
        self._create.setProperty("accent", True)
        self._create.clicked.connect(self._create_project)
        self._back = QPushButton()
        self._back.clicked.connect(self.back_requested.emit)
        buttons.addWidget(self._create)
        buttons.addWidget(self._back)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        i18n.language_changed.connect(self.retranslate)
        self.retranslate()

    def retranslate(self):
        self._title.setText(self._i18n.tr("form.title").upper())
        self._name_label.setText(self._i18n.tr("form.name"))
        self._game_label.setText(self._i18n.tr("form.game"))
        self._folder_label.setText(self._i18n.tr("form.folder"))
        self._browse.setText(self._i18n.tr("form.browse"))
        self._create.setText(self._i18n.tr("form.create"))
        self._back.setText(self._i18n.tr("form.back"))

    def _pick_folder(self):
        self._dialog = QFileDialog(self)
        self._dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self._dialog.setFileMode(QFileDialog.Directory)
        self._dialog.fileSelected.connect(self._folder.setText)
        self._dialog.show()

    def _create_project(self):
        name = NAME_PATTERN.sub("", self._name.text()).strip()
        folder = Path(self._folder.text().strip()).expanduser()
        game_id = self._game.currentData()
        if not name:
            self.message.emit(self._i18n.tr("status.invalid_name"))
            return
        if not folder.is_dir():
            self.message.emit(self._i18n.tr("status.invalid_folder"))
            return
        root = folder / name
        (root / "mods").mkdir(parents=True, exist_ok=True)
        entry = root / "mods" / "main.py"
        if not entry.exists():
            entry.write_text(TEMPLATE, encoding="utf-8")
        (root / "mod.toml").write_text(f'name = "{name}"\ngame = "{game_id}"\n', encoding="utf-8")
        self._name.clear()
        self.project_created.emit(str(root))
