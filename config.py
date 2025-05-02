# Configuration settings for the Sinhala Word Processor

# List of available fonts
FONTS = [
    "Tahoma", "Arial", "Calibri", "Times New Roman", 
    "Verdana", "Courier New", "Georgia", "Segoe UI"
]

# Available font sizes
FONT_SIZES = [
    "8", "9", "10", "11", "12", "14", "16", "18", 
    "20", "22", "24", "26", "28", "36", "48", "72"
]

# Default font size
DEFAULT_FONT_SIZE = 14

# Initial window size
INITIAL_WINDOW_SIZE = (1024, 768)

# Toolbar button configurations
TOOLBAR_BUTTONS = {
    'standard': {
        'new': {'tooltip': 'New'},
        'open': {'tooltip': 'Open'},
        'save': {'tooltip': 'Save'},
        'separator': {},
        'cut': {'tooltip': 'Cut'},
        'copy': {'tooltip': 'Copy'},
        'paste': {'tooltip': 'Paste'},
        'separator': {},
        'undo': {'tooltip': 'Undo'},
        'redo': {'tooltip': 'Redo'},
    },
    'formatting': {
        'bold': {'tooltip': 'Bold'},
        'italic': {'tooltip': 'Italic'},
        'underline': {'tooltip': 'Underline'},
        'separator': {},
        'align_left': {'tooltip': 'Align Left'},
        'align_center': {'tooltip': 'Align Center'},
        'align_right': {'tooltip': 'Align Right'},
        'separator': {},
        'bullet_list': {'tooltip': 'Bullet List'},
    }
}

# Color schemes for light and dark themes
COLOR_SCHEME = {
    'light': {
        'window_bg': '#f0f0f0',
        'window_fg': '#000000',
        'editor_bg': '#ffffff',
        'editor_fg': '#000000',
        'toolbar_bg': '#f5f5f5',
        'toolbar_fg': '#000000',
        'statusbar_bg': '#f0f0f0',
        'statusbar_fg': '#000000',
        'menu_bg': '#f0f0f0',
        'menu_fg': '#000000',
        'suggestion_bg': '#ffffff',
        'suggestion_fg': '#000000',
        'button_bg': '#e1e1e1',
        'button_fg': '#000000',
        'button_hover': '#d0d0d0',
        'scrollbar_bg': '#e1e1e1',
        'scrollbar_fg': '#c0c0c0',
        'tooltip_bg': '#FFFFE0',
        'tooltip_fg': '#000000',
        'ribbon_bg': '#f0f0f0',
        'ribbon_fg': '#000000',
        'ribbon_tab_active': '#ffffff',
        'ribbon_tab_inactive': '#e0e0e0',
    },
    'dark': {
        'window_bg': '#1e1e1e',
        'window_fg': '#ffffff',
        'editor_bg': '#2d2d2d',
        'editor_fg': '#ffffff',
        'toolbar_bg': '#333333',
        'toolbar_fg': '#ffffff',
        'statusbar_bg': '#333333',
        'statusbar_fg': '#ffffff',
        'menu_bg': '#333333',
        'menu_fg': '#ffffff',
        'suggestion_bg': '#3c3c3c',
        'suggestion_fg': '#ffffff',
        'button_bg': '#444444',
        'button_fg': '#ffffff',
        'button_hover': '#555555',
        'scrollbar_bg': '#3c3c3c',
        'scrollbar_fg': '#555555',
        'tooltip_bg': '#333333',
        'tooltip_fg': '#ffffff',
        'ribbon_bg': '#2d2d2d',
        'ribbon_fg': '#ffffff',
        'ribbon_tab_active': '#3c3c3c',
        'ribbon_tab_inactive': '#2d2d2d',
    }
}
