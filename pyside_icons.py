#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module for creating theme-aware icons in PySide6 applications,
inspired by modern UI styles like Windows 11 Fluent Design.
"""

import sys
from PySide6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QPainterPath, QFont
)
from PySide6.QtCore import Qt, QSize, QRectF, QByteArray

# Try importing QSvgRenderer for optimal rendering
try:
    from PySide6.QtSvg import QSvgRenderer
    SVG_SUPPORT = True
except ImportError:
    SVG_SUPPORT = False
    print("Warning: PySide6.QtSvg module not found. Falling back to basic QPainter rendering.")
    print("For best results, install the Qt SVG module (e.g., 'pip install PySide6-Addons')")

# Dictionary of SVG path data (d attribute) for various icons (designed for 16x16 viewBox)
# Inspired by Fluent UI / Windows 11 style - simplified and filled shapes
ICON_PATHS = {
    'new': "M4 2 C 2.895 2 2 2.895 2 4 L 2 12 C 2 13.105 2.895 14 4 14 L 9 14 L 9 13 L 4 13 C 3.448 13 3 12.552 3 12 L 3 4 C 3 3.448 3.448 3 4 3 L 9 3 L 9 6 L 12 6 L 12 8 L 13 8 L 13 5.5 L 9.5 2 L 4 2 z M 10 3.414 L 11.586 5 L 10 5 L 10 3.414 z",
    'open': "M 2 4 C 2 3.448 2.448 3 3 3 L 6.5 3 L 8 4.5 L 13 4.5 C 13.552 4.5 14 4.948 14 5.5 L 14 11.5 C 14 12.052 13.552 12.5 13 12.5 L 3 12.5 C 2.448 12.5 2 12.052 2 11.5 L 2 4 z",
    'save': "M 3 2 C 2.448 2 2 2.448 2 3 L 2 13 C 2 13.552 2.448 14 3 14 L 13 14 C 13.552 14 14 13.552 14 13 L 14 4.5 L 10.5 1 L 3 2 z M 4 3 L 10 3 L 10 6 L 4 6 L 4 3 z M 5 10 L 11 10 L 11 13 L 5 13 L 5 10 z",
    'cut': "M 4.5 2 C 3.12 2 2 3.12 2 4.5 C 2 5.88 3.12 7 4.5 7 C 5.16 7 5.75 6.77 6.2 6.4 L 8 8.2 L 9.8 6.4 C 10.25 6.77 10.84 7 11.5 7 C 12.88 7 14 5.88 14 4.5 C 14 3.12 12.88 2 11.5 2 C 10.12 2 9 3.12 9 4.5 C 9 4.64 9.02 4.78 9.05 4.9 L 6.95 4.9 C 6.98 4.78 7 4.64 7 4.5 C 7 3.12 5.88 2 4.5 2 z M 4.5 3 C 5.33 3 6 3.67 6 4.5 C 6 5.33 5.33 6 4.5 6 C 3.67 6 3 5.33 3 4.5 C 3 3.67 3.67 3 4.5 3 z M 11.5 3 C 12.33 3 13 3.67 13 4.5 C 13 5.33 12.33 6 11.5 6 C 10.67 6 10 5.33 10 4.5 C 10 3.67 10.67 3 11.5 3 z M 6.3 7 L 8 8.7 L 9.7 7 L 11.8 9.1 C 11.4 9.4 11.1 9.8 11 10.3 L 5 10.3 C 4.9 9.8 4.6 9.4 4.2 9.1 L 6.3 7 z M 4 11 L 4 14 L 6 12 L 4 11 z M 12 11 L 10 12 L 12 14 L 12 11 z",
    'copy': "M 4 2 C 3.448 2 3 2.448 3 3 L 3 11 C 3 11.552 3.448 12 4 12 L 11 12 C 11.552 12 12 11.552 12 11 L 12 3 C 12 2.448 11.552 2 11 2 L 4 2 z M 4 3 L 11 3 L 11 11 L 4 11 L 4 3 z M 13 4 L 13 13 C 13 13.552 12.552 14 12 14 L 5 14 L 5 13 L 12 13 L 12 4 L 13 4 z",
    'paste': "M 6.5 2 C 6.223 2 6 2.223 6 2.5 L 6 3 L 4 3 C 3.448 3 3 3.448 3 4 L 3 13 C 3 13.552 3.448 14 4 14 L 12 14 C 12.552 14 13 13.552 13 13 L 13 4 C 13 3.448 12.552 3 12 3 L 10 3 L 10 2.5 C 10 2.223 9.777 2 9.5 2 L 6.5 2 z M 7 3 L 9 3 L 9 4 C 9 4.552 8.552 5 8 5 C 7.448 5 7 4.552 7 4 L 7 3 z M 4 4 L 12 4 L 12 13 L 4 13 L 4 4 z",
    'undo': "M 8 3 C 4.967 3 2.459 4.935 2.053 7.811 L 2 8 L 4 8 C 4.373 6.039 5.994 4.5 8 4.5 C 10.481 4.5 12.5 6.519 12.5 9 C 12.5 11.481 10.481 13.5 8 13.5 C 5.994 13.5 4.373 11.961 4 10 L 2 10 L 2 10.189 C 2.459 13.065 4.967 15 8 15 C 11.866 15 15 11.866 15 8 C 15 4.134 11.866 1 8 1 L 8 3 z M 3.5 5 L 0.5 8 L 3.5 11 L 3.5 5 z", # Adjusted arrow and curve
    'redo': "M 8 3 L 8 1 C 4.134 1 1 4.134 1 8 C 1 11.866 4.134 15 8 15 C 11.033 15 13.541 13.065 13.947 10.189 L 14 10 L 12 10 C 11.627 11.961 10.006 13.5 8 13.5 C 5.519 13.5 3.5 11.481 3.5 9 C 3.5 6.519 5.519 4.5 8 4.5 C 10.006 4.5 11.627 6.039 12 8 L 14 8 L 14 7.811 C 13.541 4.935 11.033 3 8 3 z M 12.5 5 L 15.5 8 L 12.5 11 L 12.5 5 z", # Adjusted arrow and curve
    'theme': "M 8 1 C 4.134 1 1 4.134 1 8 C 1 11.866 4.134 15 8 15 L 8 1 z", # Half circle fill
    'keyboard': "M 2 5 C 2 4.448 2.448 4 3 4 L 13 4 C 13.552 4 14 4.448 14 5 L 14 11 C 14 11.552 13.552 12 13 12 L 3 12 C 2.448 12 2 11.552 2 11 L 2 5 z M 4 6 L 6 6 L 6 7 L 4 7 L 4 6 z M 7 6 L 9 6 L 9 7 L 7 7 L 7 6 z M 10 6 L 12 6 L 12 7 L 10 7 L 10 6 z M 4 8 L 6 8 L 6 9 L 4 9 L 4 8 z M 7 8 L 9 8 L 9 9 L 7 9 L 7 8 z M 10 8 L 12 8 L 12 9 L 10 9 L 10 8 z M 5 10 L 11 10 L 11 11 L 5 11 L 5 10 z",
    # Text formatting icons
    'bold': "M 4 2 L 4 14 L 10 14 C 11.657 14 13 12.657 13 11 C 13 9.8 12.326 8.756 11.336 8.219 C 11.758 7.709 12 7.083 12 6.4 C 12 4.525 10.475 3 8.6 3 L 4 3 L 4 2 z M 6 4 L 8.6 4 C 9.37 4 10 4.63 10 5.4 C 10 6.17 9.37 6.8 8.6 6.8 L 6 6.8 L 6 4 z M 6 8.8 L 9 8.8 C 9.77 8.8 10.4 9.43 10.4 10.2 C 10.4 10.97 9.77 11.6 9 11.6 L 6 11.6 L 6 8.8 z",
    'italic': "M 7 2 L 7 4 L 9 4 L 6 12 L 4 12 L 4 14 L 11 14 L 11 12 L 9 12 L 12 4 L 14 4 L 14 2 L 7 2 z",
    'underline': "M 4 2 L 4 9 C 4 11.761 6.239 14 9 14 C 11.761 14 14 11.761 14 9 L 14 2 L 12 2 L 12 9 C 12 10.657 10.657 12 9 12 C 7.343 12 6 10.657 6 9 L 6 2 L 4 2 z M 2 15 L 2 16 L 16 16 L 16 15 L 2 15 z",
}

# Define theme colors
THEME_COLORS = {
    'light': QColor("#202020"), # Dark gray for light background
    'dark': QColor("#E0E0E0")   # Light gray for dark background
}

def create_icon(icon_name, size=32, color=THEME_COLORS['light']):
    """
    Creates a QIcon from SVG path data, scaled and colored.
    Attempts to use QSvgRenderer first, falls back to QPainter.

    Args:
        icon_name (str): Name of the icon (must be a key in ICON_PATHS).
        size (int): Desired size of the icon in pixels.
        color (QColor): Color for the icon.

    Returns:
        QIcon: The generated icon, or an empty QIcon if name not found.
    """
    if icon_name not in ICON_PATHS:
        print(f"Error: Icon '{icon_name}' not found in ICON_PATHS.")
        return QIcon()

    path_data = ICON_PATHS[icon_name]
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    # --- Primary Method: Use QSvgRenderer if available ---
    if SVG_SUPPORT:
        try:
            # Construct the full SVG string with the dynamic fill color
            svg_data = f'''
                <svg width="16" height="16" viewBox="0 0 16 16"
                     xmlns="http://www.w3.org/2000/svg">
                    <path fill="{color.name()}" d="{path_data}"/>
                </svg>
            '''
            svg_bytes = QByteArray(svg_data.encode('utf-8'))

            renderer = QSvgRenderer(svg_bytes)
            if not renderer.isValid():
                 # Raise error to trigger fallback if SVG is bad
                 raise ValueError(f"SVG data for '{icon_name}' is invalid.")

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)

        except Exception as e:
            print(f"Warning: SVG rendering failed for '{icon_name}': {e}. Falling back.")
            # Ensure pixmap is clean for fallback
            pixmap.fill(Qt.transparent)

    # --- Fallback Method: Basic QPainter drawing (Improved visibility) ---
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Scale painter coordinate system (from 16x16) to the target pixmap size
    scale = size / 16.0
    painter.scale(scale, scale)
    # Apply a small margin so icons don't touch the edges
    margin = 1.0 # Margin in the 16x16 coordinate system
    painter.translate(margin, margin)
    scale_factor = (16.0 - 2 * margin) / 16.0
    painter.scale(scale_factor, scale_factor)


    pen = QPen(color)
    # Adjust pen width based on size for visibility, but keep it reasonable
    # Use floating point width for smoother scaling
    pen_width = max(0.75, size / 24.0) # Base width, scales slightly with size
    pen.setWidthF(pen_width)
    painter.setPen(pen)
    painter.setBrush(QBrush(color)) # Use brush for filled shapes

    # --- Reimplement drawing logic (Simplified, using color) ---
    # This part is the fallback if SVG fails or isn't supported.
    # It tries to mimic the ICON_PATHS but with basic drawing commands.
    if icon_name == "new":
        painter.setBrush(Qt.NoBrush) # Outline for paper
        painter.drawRect(3, 2, 8, 10) # Main paper
        painter.drawLine(8, 2, 8, 5)  # Fold line vertical
        painter.drawLine(8, 5, 11, 5) # Fold line horizontal
        painter.drawLine(11, 5, 11, 8) # Right edge below fold
        # Simple plus sign (optional, common for 'new')
        # painter.drawLine(5, 7, 9, 7)
        # painter.drawLine(7, 5, 7, 9)
    elif icon_name == "open":
        # Draw a simple folder shape
        painter.setBrush(color)
        painter.drawRoundedRect(1, 4, 14, 9, 1, 1) # Main folder body
        painter.drawRect(2, 2, 6, 3) # Folder tab
    elif icon_name == "save":
        painter.setBrush(color)
        painter.drawRoundedRect(2, 1, 12, 14, 1, 1) # Disk body
        # Simulate inner details with contrasting color or gaps
        painter.fillRect(3, 8, 10, 5, Qt.transparent) # Cutout at bottom
        painter.drawRect(3, 8, 10, 5)
        painter.fillRect(5, 2, 6, 4, Qt.transparent) # Top cutout/label area
        painter.drawRect(5, 2, 6, 4)
    elif icon_name == "cut":
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(2, 9, 5, 5) # Handle 1
        painter.drawEllipse(9, 9, 5, 5) # Handle 2
        painter.drawLine(4.5, 11.5, 11, 4) # Blade 1
        painter.drawLine(11.5, 11.5, 5, 4) # Blade 2
        painter.drawPoint(8, 8) # Pivot point
    elif icon_name == "copy":
        painter.setBrush(color)
        painter.drawRect(4, 4, 9, 9) # Top document
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(2, 2, 9, 9) # Bottom document (offset outline)
    elif icon_name == "paste":
        painter.setBrush(color)
        painter.drawRect(3, 4, 10, 10) # Clipboard base
        painter.drawRect(5, 2, 6, 3) # Clip part
        # Small document representation on clipboard (outline)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(5, 6, 6, 5)
        painter.drawLine(6, 8, 10, 8)
        painter.drawLine(6, 10, 9, 10)
    elif icon_name == "undo":
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(3, 3, 10, 10, 45 * 16, 270 * 16) # Arc
        # Arrow head (filled triangle)
        painter.setBrush(color)
        arrow_path = QPainterPath()
        arrow_path.moveTo(3, 8)
        arrow_path.lineTo(6, 5)
        arrow_path.lineTo(6, 11)
        arrow_path.closeSubpath()
        painter.drawPath(arrow_path)
    elif icon_name == "redo":
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(3, 3, 10, 10, -45 * 16, 270 * 16) # Arc (opposite direction)
        # Arrow head (filled triangle)
        painter.setBrush(color)
        arrow_path = QPainterPath()
        arrow_path.moveTo(13, 8)
        arrow_path.lineTo(10, 5)
        arrow_path.lineTo(10, 11)
        arrow_path.closeSubpath()
        painter.drawPath(arrow_path)
    elif icon_name == "theme":
        # Draw filled arc (half circle) for the dark part
        painter.setBrush(color)
        painter.drawPie(2, 2, 12, 12, 90 * 16, 180 * 16)
        # Draw outline for the full circle
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(2, 2, 12, 12)
    elif icon_name == "keyboard":
        painter.setBrush(color)
        painter.drawRoundedRect(1, 4, 14, 9, 1, 1) # Keyboard body
        # Simple key representations (small rectangles, maybe slightly lighter/darker)
        key_brush = QColor(color).lighter(110) if color.lightnessF() > 0.5 else QColor(color).darker(110)
        painter.setBrush(key_brush)
        painter.setPen(Qt.NoPen) # No outline for keys
        painter.drawRect(3, 5.5, 2, 1.5)
        painter.drawRect(6, 5.5, 2, 1.5)
        painter.drawRect(9, 5.5, 2, 1.5)
        painter.drawRect(3, 8, 2, 1.5)
        painter.drawRect(6, 8, 2, 1.5)
        painter.drawRect(9, 8, 2, 1.5)
        painter.drawRect(4, 10.5, 8, 1.5) # Space bar
    elif icon_name == "bold":
        # Draw a bold 'B'
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(QRectF(0, 0, 16, 16), Qt.AlignCenter, "B")
    elif icon_name == "italic":
        # Draw an italic 'I'
        font = QFont("Arial", 12)
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, 16, 16), Qt.AlignCenter, "I")
    elif icon_name == "underline":
        # Draw an underlined 'U'
        painter.setFont(QFont("Arial", 12))
        painter.drawText(QRectF(0, 0, 16, 14), Qt.AlignCenter, "U")
        # Draw the underline
        painter.drawLine(4, 14, 12, 14)
    else:
        # Draw a fallback question mark if icon name has no specific drawing
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(QRectF(0, 0, 16, 16), Qt.AlignCenter, "?")

    painter.end()
    return QIcon(pixmap)


def get_toolbar_icon(icon_name, theme='light', size=32):
    """
    Get a toolbar icon as a QIcon, adapting to the theme.

    Args:
        icon_name (str): Name of the icon (key in ICON_PATHS).
        theme (str): 'light' or 'dark'. Determines the icon color.
        size (int): Desired icon size in pixels.

    Returns:
        QIcon: Icon for the given name and theme.
    """
    color = THEME_COLORS.get(theme, THEME_COLORS['light'])
    return create_icon(icon_name, size=size, color=color)