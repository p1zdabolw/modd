STYLESHEET = """
* {
    outline: none;
}
QWidget {
    background: #16161e;
    color: #c0caf5;
    font-family: "Segoe UI", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 13px;
}
QPlainTextEdit {
    background: #14151f;
    color: #c0caf5;
    border: none;
    selection-background-color: #33467c;
    selection-color: #e8ecff;
    font-family: "JetBrains Mono", "Cascadia Mono", "Consolas", "DejaVu Sans Mono", monospace;
    font-size: 12px;
}
QToolBar {
    background: #16161e;
    border: none;
    padding: 8px;
    spacing: 6px;
}
QToolBar::separator {
    background: #23263a;
    width: 1px;
    margin: 4px 6px;
}
QToolBar QToolButton {
    background: #1f2233;
    color: #c0caf5;
    border: 1px solid #2a2d42;
    border-radius: 6px;
    padding: 6px 14px;
}
QToolBar QToolButton:hover {
    background: #2a2d42;
    border-color: #3d4266;
}
QToolBar QToolButton:pressed {
    background: #24283b;
}
QToolBar QToolButton:checked {
    background: #2f3757;
    color: #e8ecff;
    border-color: #4a5897;
}
QToolBar QToolButton:disabled {
    color: #4b5170;
    background: #1a1b26;
    border-color: #23263a;
}
QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    color: #9aa3cf;
}
QToolButton:hover {
    background: #1f2233;
    color: #c0caf5;
}
QToolButton:checked {
    background: #2f3757;
    color: #e8ecff;
    border-color: #4a5897;
}
QPushButton {
    background: #1f2233;
    color: #c0caf5;
    border: 1px solid #2a2d42;
    border-radius: 6px;
    padding: 6px 14px;
}
QPushButton:hover {
    background: #2a2d42;
    border-color: #3d4266;
}
QPushButton:pressed {
    background: #24283b;
}
QPushButton:disabled {
    color: #4b5170;
    background: #1a1b26;
    border-color: #23263a;
}
QPushButton[accent="true"] {
    background: #7aa2f7;
    color: #12141d;
    border: none;
    font-weight: 600;
}
QPushButton[accent="true"]:hover {
    background: #93b3fa;
}
QPushButton[accent="true"]:pressed {
    background: #6b93e8;
}
QLineEdit, QComboBox {
    background: #1a1b26;
    border: 1px solid #2a2d42;
    border-radius: 6px;
    padding: 6px 8px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #7aa2f7;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background: #1a1b26;
    border: 1px solid #2a2d42;
    selection-background-color: #2f3757;
    outline: 0;
}
QTreeView, QTreeWidget, QListView {
    background: #1a1b26;
    alternate-background-color: #191b28;
    border: 1px solid #23263a;
    border-radius: 8px;
    outline: 0;
}
QTreeView::item, QTreeWidget::item {
    padding: 3px 4px;
}
QTreeView::item:hover, QTreeWidget::item:hover {
    background: #23263a;
}
QTreeView::item:selected, QTreeWidget::item:selected {
    background: #2f3757;
    color: #e8ecff;
}
QHeaderView::section {
    background: #12131c;
    color: #7a82ad;
    border: none;
    border-bottom: 1px solid #23263a;
    padding: 6px 8px;
    font-weight: 600;
}
QTabWidget::pane {
    border: 1px solid #23263a;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: #7a82ad;
    padding: 7px 14px;
    margin: 2px 2px 0 0;
    border: 1px solid transparent;
    border-radius: 6px;
}
QTabBar::tab:selected {
    background: #1a1b26;
    color: #c0caf5;
    border-color: #23263a;
}
QTabBar::tab:hover:!selected {
    background: #1c1e2e;
    color: #a8b0d8;
}
QSplitter::handle {
    background: #10111a;
}
QSplitter::handle:hover {
    background: #2f3757;
}
QSplitter::handle:horizontal {
    width: 4px;
}
QSplitter::handle:vertical {
    height: 4px;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #2a2d42;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #3d4266;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #2a2d42;
    min-width: 30px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #3d4266;
}
QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
    border: none;
    width: 0;
    height: 0;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}
QStatusBar {
    background: #12131c;
    color: #8b93b8;
    border-top: 1px solid #1f2233;
}
QStatusBar::item {
    border: none;
}
QLabel#panelTitle {
    background: transparent;
    color: #7a82ad;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}
QToolTip {
    background: #1f2233;
    color: #c0caf5;
    border: 1px solid #2a2d42;
    padding: 4px 8px;
}
"""
