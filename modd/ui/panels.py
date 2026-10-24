from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ProblemsPanel(QTreeWidget):
    location_requested = Signal(str, int)

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        self.setColumnCount(3)
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.setWordWrap(False)
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.itemDoubleClicked.connect(self._emit_location)
        i18n.language_changed.connect(self.retranslate)
        self.retranslate()

    def retranslate(self):
        self.setHeaderLabels(
            [self._i18n.tr("col.file"), self._i18n.tr("col.line"), self._i18n.tr("col.message")]
        )

    def set_file_errors(self, path, errors):
        self._remove_path(path)
        for line, message in errors:
            item = QTreeWidgetItem([Path(path).name, str(line), message])
            item.setData(0, Qt.ItemDataRole.UserRole, path)
            item.setData(1, Qt.ItemDataRole.UserRole, line)
            self.addTopLevelItem(item)

    def add_entry(self, origin, message):
        item = QTreeWidgetItem([origin, "-", message])
        item.setData(0, Qt.ItemDataRole.UserRole, "")
        item.setData(1, Qt.ItemDataRole.UserRole, 0)
        self.addTopLevelItem(item)

    def _remove_path(self, path):
        for index in reversed(range(self.topLevelItemCount())):
            item = self.topLevelItem(index)
            if item.data(0, Qt.ItemDataRole.UserRole) == path:
                self.takeTopLevelItem(index)

    def _emit_location(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        line = item.data(1, Qt.ItemDataRole.UserRole)
        if path:
            self.location_requested.emit(path, int(line))


class DebuggerPanel(QWidget):
    step_over_clicked = Signal()
    step_into_clicked = Signal()
    step_out_clicked = Signal()
    continue_clicked = Signal()
    stack_location_requested = Signal(str, int)

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)
        self._title = QLabel()
        self._title.setObjectName("panelTitle")
        layout.addWidget(self._title)
        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        self._step_over = QPushButton()
        self._step_into = QPushButton()
        self._step_out = QPushButton()
        self._continue = QPushButton()
        self._step_over.clicked.connect(self.step_over_clicked.emit)
        self._step_into.clicked.connect(self.step_into_clicked.emit)
        self._step_out.clicked.connect(self.step_out_clicked.emit)
        self._continue.clicked.connect(self.continue_clicked.emit)
        for button in (self._step_over, self._step_into, self._step_out, self._continue):
            buttons.addWidget(button)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self._stack_title = QLabel()
        self._stack_title.setObjectName("panelTitle")
        layout.addWidget(self._stack_title)
        self._stack = QTreeWidget()
        self._stack.setRootIsDecorated(False)
        self._stack.setUniformRowHeights(True)
        self._stack.itemDoubleClicked.connect(self._emit_stack_location)
        layout.addWidget(self._stack, 2)
        self._locals_title = QLabel()
        self._locals_title.setObjectName("panelTitle")
        layout.addWidget(self._locals_title)
        self._locals = QTreeWidget()
        self._locals.setRootIsDecorated(False)
        self._locals.setUniformRowHeights(True)
        layout.addWidget(self._locals, 3)
        self.set_active(False)
        i18n.language_changed.connect(self.retranslate)
        self.retranslate()

    def retranslate(self):
        self._title.setText(self._i18n.tr("panel.debugger").upper())
        self._stack_title.setText(self._i18n.tr("panel.stack").upper())
        self._locals_title.setText(self._i18n.tr("panel.variables").upper())
        self._step_over.setText(self._i18n.tr("debug.step_over"))
        self._step_into.setText(self._i18n.tr("debug.step_into"))
        self._step_out.setText(self._i18n.tr("debug.step_out"))
        self._continue.setText(self._i18n.tr("debug.continue"))
        self._stack.setHeaderLabels(
            [self._i18n.tr("col.function"), self._i18n.tr("col.file"), self._i18n.tr("col.line")]
        )
        self._locals.setHeaderLabels([self._i18n.tr("col.name"), self._i18n.tr("col.value")])

    def set_active(self, active):
        for button in (self._step_over, self._step_into, self._step_out, self._continue):
            button.setEnabled(active)

    def update_stack(self, frames):
        self._stack.clear()
        for name, file, line in frames:
            item = QTreeWidgetItem([name, Path(file).name, str(line)])
            item.setData(0, Qt.ItemDataRole.UserRole, file)
            item.setData(1, Qt.ItemDataRole.UserRole, line)
            self._stack.addTopLevelItem(item)

    def update_locals(self, values):
        self._locals.clear()
        for key in sorted(values):
            self._locals.addTopLevelItem(QTreeWidgetItem([key, values[key]]))

    def _emit_stack_location(self, item, column):
        file = item.data(0, Qt.ItemDataRole.UserRole)
        line = item.data(1, Qt.ItemDataRole.UserRole)
        if file:
            self.stack_location_requested.emit(file, int(line))


class ConsolePanel(QWidget):
    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self._i18n = i18n
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 8)
        layout.setSpacing(6)
        header = QHBoxLayout()
        header.setSpacing(6)
        self._title = QLabel()
        self._title.setObjectName("panelTitle")
        header.addWidget(self._title)
        header.addStretch(1)
        self._clear = QPushButton()
        self._clear.clicked.connect(self._view_clear)
        header.addWidget(self._clear)
        layout.addLayout(header)
        self._view = QPlainTextEdit()
        self._view.setReadOnly(True)
        self._view.setMaximumBlockCount(5000)
        layout.addWidget(self._view)
        i18n.language_changed.connect(self.retranslate)
        self.retranslate()

    def retranslate(self):
        self._title.setText(self._i18n.tr("panel.console").upper())
        self._clear.setText(self._i18n.tr("console.clear"))

    def append_output(self, text):
        cursor = self._view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self._view.setTextCursor(cursor)
        self._view.ensureCursorVisible()

    def _view_clear(self):
        self._view.clear()
