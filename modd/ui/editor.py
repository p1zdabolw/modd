import ast

from pathlib import Path

from PySide6.QtCore import QRegularExpression, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget


def _format(color, bold=False, italic=False):
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(color))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


def analyze(source):
    try:
        ast.parse(source)
    except SyntaxError as error:
        return [(error.lineno or 1, error.msg)]
    return []


class PythonHighlighter(QSyntaxHighlighter):
    KEYWORDS = (
        "and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|"
        "for|from|global|if|import|in|is|lambda|nonlocal|not|or|raise|return|try|while|with|yield"
    )
    BUILTINS = (
        "abs|all|any|bool|dict|dir|enumerate|filter|float|getattr|hasattr|input|int|"
        "isinstance|len|list|map|max|min|next|object|open|print|range|repr|reversed|round|"
        "self|set|setattr|sorted|str|sum|super|tuple|type|zip"
    )

    def __init__(self, document):
        super().__init__(document)
        self._rules = [
            (QRegularExpression(rf"\b(?:{self.KEYWORDS})\b"), _format("#bb9af7")),
            (
                QRegularExpression(r"(?<=\bdef )\w+|(?<=\bclass )\w+"),
                _format("#7aa2f7", bold=True),
            ),
            (QRegularExpression(rf"\b(?:{self.BUILTINS})\b"), _format("#4fd6be")),
            (QRegularExpression(r"\b\d+(?:\.\d+)?\b"), _format("#ff9e64")),
            (QRegularExpression(r"@\w+"), _format("#e0af68")),
        ]
        self._string_format = _format("#9ece6a")
        self._comment_format = _format("#565f89", italic=True)

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
        self._paint_strings(text)

    def _paint_strings(self, text):
        state = self.previousBlockState()
        if state < 0:
            state = 0
        length = len(text)
        position = 0
        while position < length:
            if state in (1, 2):
                closer = "'''" if state == 1 else '"""'
                index = text.find(closer, position)
                if index < 0:
                    self.setFormat(position, length - position, self._string_format)
                    position = length
                else:
                    self.setFormat(position, index + 3 - position, self._string_format)
                    position = index + 3
                    state = 0
                continue
            char = text[position]
            if char == "#":
                self.setFormat(position, length - position, self._comment_format)
                break
            triple = 0
            if text.startswith("'''", position):
                triple = 1
            elif text.startswith('"""', position):
                triple = 2
            if triple:
                end = text.find("'''" if triple == 1 else '"""', position + 3)
                if end < 0:
                    self.setFormat(position, length - position, self._string_format)
                    state = triple
                    position = length
                else:
                    self.setFormat(position, end + 3 - position, self._string_format)
                    position = end + 3
                continue
            if char in ("'", '"'):
                cursor = position + 1
                while cursor < length:
                    if text[cursor] == "\\":
                        cursor += 2
                        continue
                    if text[cursor] == char:
                        break
                    cursor += 1
                span = cursor + 1 - position if cursor < length else length - position
                self.setFormat(position, span, self._string_format)
                position += span
                continue
            position += 1
        self.setCurrentBlockState(state)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_width(), 0)

    def paintEvent(self, event):
        self._editor.paint_line_numbers(event)

    def mousePressEvent(self, event):
        self._editor.toggle_breakpoint_at(event.position().toPoint())


class CodeEditor(QPlainTextEdit):
    analysis_finished = Signal(str, list)
    breakpoints_changed = Signal(str, object)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self._path = str(Path(path).resolve())
        self._errors = []
        self._breakpoints = set()
        self._debug_line = 0
        self._line_area = LineNumberArea(self)
        self._highlighter = PythonHighlighter(self.document())
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(400)
        timer.timeout.connect(self.reanalyze)
        self.textChanged.connect(timer.start)
        self.blockCountChanged.connect(self._update_line_area_width)
        self.updateRequest.connect(self._update_line_area)
        self.cursorPositionChanged.connect(self._rebuild_selections)
        self._update_line_area_width()

    def path(self):
        return self._path

    def breakpoints(self):
        return set(self._breakpoints)

    def reanalyze(self):
        self._errors = analyze(self.toPlainText())
        self._rebuild_selections()
        self.analysis_finished.emit(self._path, list(self._errors))

    def set_debug_line(self, line):
        self._debug_line = line
        self._rebuild_selections()
        if line:
            self.jump_to(line)

    def toggle_breakpoint_at(self, position):
        cursor = self.cursorForPosition(position)
        line = cursor.blockNumber() + 1
        if line in self._breakpoints:
            self._breakpoints.discard(line)
        else:
            self._breakpoints.add(line)
        self._line_area.update()
        self.breakpoints_changed.emit(self._path, set(self._breakpoints))

    def jump_to(self, line):
        block = self.document().findBlockByNumber(line - 1)
        if not block.isValid():
            return
        self.setTextCursor(QTextCursor(block))
        self.centerCursor()
        self.setFocus()

    def line_number_width(self):
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def paint_line_numbers(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), QColor("#12131c"))
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        current = self.textCursor().blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                height = self.fontMetrics().height()
                color = "#c0caf5" if number == current else "#565f89"
                if number + 1 == self._debug_line:
                    color = "#9ece6a"
                elif number + 1 in self._breakpoints:
                    color = "#f38ba8"
                painter.setPen(QColor(color))
                painter.drawText(0, top, self._line_area.width() - 8, height, Qt.AlignmentFlag.AlignRight, str(number + 1))
                if number + 1 in self._breakpoints:
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor("#f38ba8"))
                    painter.drawEllipse(4, top + height // 2 - 4, 8, 8)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            number += 1
        painter.end()

    def showEvent(self, event):
        super().showEvent(event)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        contents = self.contentsRect()
        self._line_area.setGeometry(QRect(contents.left(), contents.top(), self.line_number_width(), contents.height()))

    def _update_line_area_width(self, count=0):
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def _update_line_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_area_width()

    def _rebuild_selections(self):
        selections = []
        cursor_line = self.textCursor().blockNumber() + 1
        if self._debug_line:
            selections.append(self._line_selection(self._debug_line, QColor("#28352a")))
        for line, message in self._errors:
            selections.append(self._line_selection(line, QColor("#33232d")))
            wave = self._wave_selection(line)
            if wave is not None:
                selections.append(wave)
        if not self.isReadOnly():
            selections.append(self._line_selection(cursor_line, QColor("#1c1e2e")))
        self.setExtraSelections(selections)

    def _line_selection(self, line, color):
        block = self.document().findBlockByNumber(line - 1)
        if not block.isValid():
            block = self.document().lastBlock()
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(color)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = QTextCursor(block)
        return selection

    def _wave_selection(self, line):
        block = self.document().findBlockByNumber(line - 1)
        if not block.isValid():
            return None
        cursor = QTextCursor(block)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        selection = QTextEdit.ExtraSelection()
        selection.cursor = cursor
        selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        selection.format.setUnderlineColor(QColor("#f38ba8"))
        return selection
