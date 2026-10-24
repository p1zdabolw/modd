import tomllib

from functools import partial
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFileSystemModel,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QToolBar,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from modd.core.game_adapter import ModPackage
from modd.debugger.runner import Session
from modd.debugger.tracer import TracerBridge
from modd.ui.create_project import CreateProjectPanel
from modd.ui.editor import CodeEditor
from modd.ui.icon import build_app_icon
from modd.ui.panels import ConsolePanel, DebuggerPanel, ProblemsPanel

TEXT_SUFFIXES = {".py", ".toml", ".json", ".txt", ".ini", ".cfg", ".yml", ".yaml"}


class MainWindow(QMainWindow):
    def __init__(self, registry, i18n):
        super().__init__()
        self._registry = registry
        self._i18n = i18n
        self._session = None
        self._tracer = None
        self._bridge = None
        self._project_root = None
        self._project_name = ""
        self._adapter = None
        self._editors = {}
        self._debug_editor = None
        self._dialog = None
        self.setWindowIcon(build_app_icon())
        self.resize(1520, 920)
        self.setMinimumSize(1180, 720)
        self._actions = {}
        self._build_toolbar()
        self._build_body()
        save_shortcut = QShortcut(QKeySequence(QKeySequence.StandardKey.Save), self)
        save_shortcut.activated.connect(self._save_current)
        i18n.language_changed.connect(self.retranslate)
        self.retranslate()

    def _build_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(toolbar)
        entries = (
            ("action.create_project", self._toggle_create_panel),
            ("action.open_project", self._open_project_dialog),
        )
        for key, slot in entries:
            action = QAction(toolbar)
            action.triggered.connect(slot)
            toolbar.addAction(action)
            self._actions[key] = action
        toolbar.addSeparator()
        for key, slot in (
            ("action.run", self._run_current),
            ("action.debug", self._debug_current),
            ("action.stop", self._stop_session),
        ):
            action = QAction(toolbar)
            action.triggered.connect(slot)
            toolbar.addAction(action)
            self._actions[key] = action
        toolbar.addSeparator()
        for key, slot in (
            ("action.build", self._build_project),
            ("action.deploy", self._deploy_project),
        ):
            action = QAction(toolbar)
            action.triggered.connect(slot)
            toolbar.addAction(action)
            self._actions[key] = action
        self._actions["action.stop"].setEnabled(False)
        self._actions["action.build"].setEnabled(False)
        self._actions["action.deploy"].setEnabled(False)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        self._language_group = QButtonGroup(self)
        self._language_group.setExclusive(True)
        self._language_buttons = {}
        for code in ("en", "ru"):
            button = QToolButton()
            button.setText(code.upper())
            button.setCheckable(True)
            button.setChecked(self._i18n.language() == code)
            button.clicked.connect(partial(self._i18n.set_language, code))
            self._language_group.addButton(button)
            self._language_buttons[code] = button
            toolbar.addWidget(button)

    def _build_body(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        self._tree_model = QFileSystemModel(self)
        self._tree = QTreeView()
        self._tree.setModel(self._tree_model)
        self._tree.setHeaderHidden(True)
        for column in range(1, 4):
            self._tree.hideColumn(column)
        self._tree.doubleClicked.connect(self._open_from_tree)
        project_page = QWidget()
        project_layout = QVBoxLayout(project_page)
        project_layout.setContentsMargins(8, 6, 8, 8)
        project_layout.setSpacing(6)
        self._project_title = QLabel()
        self._project_title.setObjectName("panelTitle")
        project_layout.addWidget(self._project_title)
        project_layout.addWidget(self._tree)
        self._create_panel = CreateProjectPanel(self._registry, self._i18n)
        self._create_panel.project_created.connect(self._attach_project)
        self._create_panel.back_requested.connect(self._show_tree)
        self._create_panel.message.connect(self._show_status)
        self._side_stack = QStackedWidget()
        self._side_stack.addWidget(project_page)
        self._side_stack.addWidget(self._create_panel)
        splitter.addWidget(self._side_stack)
        center = QSplitter(Qt.Orientation.Vertical)
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        self._console = ConsolePanel(self._i18n)
        center.addWidget(self._tabs)
        center.addWidget(self._console)
        center.setSizes([620, 240])
        splitter.addWidget(center)
        right = QSplitter(Qt.Orientation.Vertical)
        self._problems = ProblemsPanel(self._i18n)
        self._problems.location_requested.connect(self._reveal_location)
        self._debugger = DebuggerPanel(self._i18n)
        self._debugger.step_over_clicked.connect(partial(self._request_step, "over"))
        self._debugger.step_into_clicked.connect(partial(self._request_step, "into"))
        self._debugger.step_out_clicked.connect(partial(self._request_step, "out"))
        self._debugger.continue_clicked.connect(partial(self._request_step, "continue"))
        self._debugger.stack_location_requested.connect(self._reveal_location)
        right.addWidget(self._problems)
        right.addWidget(self._debugger)
        right.setSizes([300, 420])
        splitter.addWidget(right)
        splitter.setSizes([300, 880, 340])
        splitter.setStretchFactor(1, 1)

    def retranslate(self):
        self.setWindowTitle(self._i18n.tr("window.title"))
        for key, action in self._actions.items():
            action.setText(self._i18n.tr(key))
        self._project_title.setText(self._i18n.tr("panel.project").upper())

    def _show_status(self, text):
        self.statusBar().showMessage(text, 8000)

    def _current_editor(self):
        widget = self._tabs.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None

    def _toggle_create_panel(self):
        if self._side_stack.currentIndex() == 1:
            self._show_tree()
        else:
            self._side_stack.setCurrentIndex(1)

    def _show_tree(self):
        self._side_stack.setCurrentIndex(0)

    def _open_project_dialog(self):
        self._dialog = QFileDialog(self)
        self._dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self._dialog.setFileMode(QFileDialog.Directory)
        self._dialog.fileSelected.connect(self._attach_project)
        self._dialog.show()

    def _attach_project(self, path):
        root = Path(path).resolve()
        self._project_root = root
        self._project_name = root.name
        self._tree_model.setRootPath(str(root))
        self._tree.setRootIndex(self._tree_model.index(str(root)))
        self._adapter = self._detect_adapter(root)
        self._show_tree()
        self._show_status(self._i18n.tr("status.project_opened", path=str(root)))
        if self._adapter is not None:
            self._show_status(self._i18n.tr("status.adapter", adapter=self._adapter.title))
        else:
            self._show_status(self._i18n.tr("status.no_adapter", path=self._project_name))
        self._actions["action.build"].setEnabled(self._adapter is not None)
        self._actions["action.deploy"].setEnabled(self._adapter is not None)
        entry = root / "mods" / "main.py"
        if entry.is_file():
            self.open_file(entry)

    def _detect_adapter(self, root):
        manifest = root / "mod.toml"
        if manifest.is_file():
            try:
                with manifest.open("rb") as stream:
                    data = tomllib.load(stream)
            except tomllib.TOMLDecodeError as error:
                self._problems.add_entry("mod.toml", str(error))
                data = {}
            game_id = data.get("game")
            if game_id:
                adapter = self._registry.by_id(game_id)
                if adapter is not None:
                    return adapter
        for adapter in self._registry.adapters():
            if adapter.detect(root):
                return adapter
        return None

    def _open_from_tree(self, index):
        path = Path(self._tree_model.filePath(index))
        if path.is_file():
            self.open_file(path)

    def open_file(self, path):
        path = Path(path).resolve()
        key = str(path)
        if key in self._editors:
            editor = self._editors[key]
            self._tabs.setCurrentWidget(editor)
            return editor
        if path.suffix.lower() not in TEXT_SUFFIXES:
            self._show_status(self._i18n.tr("status.unsupported_file"))
            return None
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            self._problems.add_entry(path.name, str(error))
            return None
        editor = CodeEditor(key)
        editor.analysis_finished.connect(self._update_problems)
        editor.breakpoints_changed.connect(self._sync_breakpoints)
        editor.setPlainText(content)
        self._tabs.addTab(editor, path.name)
        self._tabs.setCurrentWidget(editor)
        self._editors[key] = editor
        editor.reanalyze()
        return editor

    def _close_tab(self, index):
        editor = self._tabs.widget(index)
        if isinstance(editor, CodeEditor):
            editor.analysis_finished.disconnect(self._update_problems)
            editor.breakpoints_changed.disconnect(self._sync_breakpoints)
            self._problems.set_file_errors(editor.path(), [])
            if self._debug_editor is editor:
                self._debug_editor = None
            del self._editors[editor.path()]
        self._tabs.removeTab(index)
        if isinstance(editor, CodeEditor):
            editor.deleteLater()

    def _update_problems(self, path, errors):
        self._problems.set_file_errors(path, errors)

    def _reveal_location(self, path, line):
        editor = self.open_file(path)
        if editor is not None:
            editor.jump_to(line)

    def _save_current(self):
        editor = self._current_editor()
        if editor is None:
            return
        Path(editor.path()).write_text(editor.toPlainText(), encoding="utf-8")
        self._show_status(self._i18n.tr("status.saved", file=Path(editor.path()).name))

    def _run_current(self):
        self._start_session(debug=False)

    def _debug_current(self):
        self._start_session(debug=True)

    def _start_session(self, debug):
        if self._session is not None:
            return
        editor = self._current_editor()
        if editor is None or not editor.path().endswith(".py"):
            self._show_status(self._i18n.tr("status.no_python_file"))
            return
        bridge = TracerBridge()
        bridge.output.connect(self._console.append_output)
        bridge.location.connect(self._on_location)
        bridge.stack_changed.connect(self._debugger.update_stack)
        bridge.locals_changed.connect(self._debugger.update_locals)
        bridge.finished.connect(self._on_finished)
        self._bridge = bridge
        self._session = Session(editor.path(), editor.toPlainText(), bridge, debug)
        if debug:
            self._tracer = self._session.tracer
            for path, source_editor in self._editors.items():
                for line in source_editor.breakpoints():
                    self._tracer.set_break(path, line)
        self._actions["action.run"].setEnabled(False)
        self._actions["action.debug"].setEnabled(False)
        self._actions["action.stop"].setEnabled(debug)
        self._debugger.set_active(False)
        self._show_status(self._i18n.tr("status.running", file=Path(editor.path()).name))
        self._session.start()

    def _on_location(self, file, line):
        editor = self.open_file(file)
        if editor is None:
            return
        if self._debug_editor is not None and self._debug_editor is not editor:
            self._debug_editor.set_debug_line(0)
        self._debug_editor = editor
        editor.set_debug_line(line)
        self._debugger.set_active(True)
        self._show_status(self._i18n.tr("status.paused", file=Path(file).name, line=line))

    def _request_step(self, action):
        if self._tracer is None:
            return
        self._debugger.set_active(False)
        self._tracer.request(action)

    def _sync_breakpoints(self, path, lines):
        if self._tracer is None:
            return
        self._tracer.clear_all_breaks()
        for editor_path, editor in self._editors.items():
            for line in editor.breakpoints():
                self._tracer.set_break(editor_path, line)

    def _stop_session(self):
        if self._session is not None and self._tracer is not None:
            self._tracer.interrupt()

    def _on_finished(self, code):
        self._session = None
        self._tracer = None
        self._bridge = None
        self._debugger.set_active(False)
        self._debugger.update_stack([])
        self._debugger.update_locals({})
        if self._debug_editor is not None:
            self._debug_editor.set_debug_line(0)
            self._debug_editor = None
        self._actions["action.run"].setEnabled(True)
        self._actions["action.debug"].setEnabled(True)
        self._actions["action.stop"].setEnabled(False)
        self._show_status(self._i18n.tr("status.finished", code=code))

    def _guard_project(self):
        if self._project_root is None:
            self._show_status(self._i18n.tr("status.no_project"))
            return True
        if self._adapter is None:
            self._show_status(self._i18n.tr("status.no_adapter", path=self._project_name))
            return True
        return False

    def _build_project(self):
        if self._guard_project():
            return
        package = ModPackage(self._project_root, self._project_name, self._adapter.game_id)
        self._show_status(self._i18n.tr("status.build_started", name=self._project_name))
        self._run_adapter_operation(package, self._adapter.build, "status.build_done")

    def _deploy_project(self):
        if self._guard_project():
            return
        package = ModPackage(self._project_root, self._project_name, self._adapter.game_id)
        self._show_status(self._i18n.tr("status.deploy_started", name=self._project_name))
        self._run_adapter_operation(package, self._adapter.deploy, "status.deploy_done")

    def _run_adapter_operation(self, package, operation, done_key):
        problems = self._adapter.validate(package)
        if problems:
            for file, line, message in problems:
                self._problems.add_entry(Path(file).name, message)
            return
        try:
            result = operation(package)
        except NotImplementedError:
            self._problems.add_entry(
                self._adapter.game_id,
                self._i18n.tr(
                    "problems.unavailable", title=self._adapter.title, method=operation.__name__
                ),
            )
            return
        self._show_status(self._i18n.tr(done_key, path=result))
