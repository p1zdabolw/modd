import struct

from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap

ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
ICO_SIZES = (16, 32, 48, 64, 128, 256)


def draw_logo(size):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    margin = size * 0.05
    radius = size * 0.24
    rect = QRectF(margin, margin, size - margin * 2, size - margin * 2)
    background = QLinearGradient(rect.topLeft(), rect.bottomRight())
    background.setColorAt(0.0, QColor("#2b2f4c"))
    background.setColorAt(1.0, QColor("#14151f"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(background)
    painter.drawRoundedRect(rect, radius, radius)
    top = size * 0.33
    bottom = size * 0.70
    left = size * 0.30
    right = size * 0.70
    middle_x = (left + right) / 2
    middle_y = size * 0.60
    ink = QLinearGradient(0, top, 0, bottom)
    ink.setColorAt(0.0, QColor("#9cb8fd"))
    ink.setColorAt(1.0, QColor("#5d84dd"))
    pen = QPen(QBrush(ink), size * 0.125)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    path = QPainterPath()
    path.moveTo(left, bottom)
    path.lineTo(left, top)
    path.lineTo(middle_x, middle_y)
    path.lineTo(right, top)
    path.lineTo(right, bottom)
    painter.drawPath(path)
    painter.end()
    return pixmap


def build_app_icon():
    icon = QIcon()
    for size in ICON_SIZES:
        icon.addPixmap(draw_logo(size))
    return icon


def save_ico(path):
    images = []
    for size in ICO_SIZES:
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        draw_logo(size).save(buffer, "PNG")
        images.append(bytes(buffer.data()))
        buffer.close()
    header = struct.pack("<HHH", 0, 1, len(images))
    entries = b""
    body = b""
    offset = 6 + 16 * len(images)
    for size, image in zip(ICO_SIZES, images):
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(image), offset)
        offset += len(image)
        body += image
    Path(path).write_bytes(header + entries + body)
