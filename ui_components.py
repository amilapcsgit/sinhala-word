import tkinter as tk
from tkinter import font as tkfont
import customtkinter as ctk
import os

from config import FONTS, FONT_SIZES, TOOLBAR_BUTTONS, COLOR_SCHEME
from icons import get_toolbar_icon

def create_menu(root, app):
    """Create the main menu bar for the application"""
    menu_bar = tk.Menu(root)

    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New", accelerator="Ctrl+N", command=app.new_file)
    file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=app.open_file)
    file_menu.add_command(label="Save", accelerator="Ctrl+S", command=app.save_file)
    file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=app.save_as_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.on_closing)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Edit menu
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", 
                         command=lambda: app.text_area.event_generate("<<Undo>>"))
    edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", 
                         command=lambda: app.text_area.event_generate("<<Redo>>"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", accelerator="Ctrl+X", 
                         command=lambda: app.text_area.event_generate("<<Cut>>"))
    edit_menu.add_command(label="Copy", accelerator="Ctrl+C", 
                         command=lambda: app.text_area.event_generate("<<Copy>>"))
    edit_menu.add_command(label="Paste", accelerator="Ctrl+V", 
                         command=lambda: app.text_area.event_generate("<<Paste>>"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", accelerator="Ctrl+A", 
                         command=lambda: app.text_area.tag_add(tk.SEL, "1.0", tk.END))
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # View menu
    view_menu = tk.Menu(menu_bar, tearoff=0)
    view_menu.add_command(label="Toggle Theme", command=app.toggle_theme)
    view_menu.add_command(label="Toggle Toolbars", command=app.toggle_toolbars)
    view_menu.add_command(label="Toggle Keyboard", command=app.toggle_keyboard)
    menu_bar.add_cascade(label="View", menu=view_menu)

    # Set the menu
    root.config(menu=menu_bar)

    # Bind keyboard shortcuts
    root.bind("<Control-n>", lambda event: app.new_file())
    root.bind("<Control-o>", lambda event: app.open_file())
    root.bind("<Control-s>", lambda event: app.save_file())
    root.bind("<Control-S>", lambda event: app.save_as_file())

    return menu_bar

def create_toolbars(parent, app):
    """Create standard and formatting toolbars"""
    # Standard toolbar
    standard_frame = ctk.CTkFrame(parent)
    standard_frame.pack(fill=tk.X, side=tk.TOP)

    # Create standard toolbar buttons
    for btn_id, btn_data in TOOLBAR_BUTTONS['standard'].items():
        if btn_id == 'separator':
            create_separator(standard_frame)
            continue

        # Define separate functions to avoid lambda capturing issues
        if btn_id == 'new':
            def new_cmd(): return app.new_file()
            command = new_cmd
        elif btn_id == 'open':
            def open_cmd(): return app.open_file()
            command = open_cmd
        elif btn_id == 'save':
            def save_cmd(): return app.save_file()
            command = save_cmd
        elif btn_id == 'cut':
            def cut_cmd(): return app.text_area.event_generate("<<Cut>>")
            command = cut_cmd
        elif btn_id == 'copy':
            def copy_cmd(): return app.text_area.event_generate("<<Copy>>")
            command = copy_cmd
        elif btn_id == 'paste':
            def paste_cmd(): return app.text_area.event_generate("<<Paste>>")
            command = paste_cmd
        elif btn_id == 'undo':
            def undo_cmd(): return app.text_area.event_generate("<<Undo>>")
            command = undo_cmd
        elif btn_id == 'redo':
            def redo_cmd(): return app.text_area.event_generate("<<Redo>>")
            command = redo_cmd
        else:
            command = None

        create_toolbar_button(standard_frame, btn_id, btn_data['tooltip'], command)

    # Formatting toolbar
    formatting_frame = ctk.CTkFrame(parent)
    formatting_frame.pack(fill=tk.X, side=tk.TOP)

    # Font selector
    font_label = ctk.CTkLabel(formatting_frame, text="Font:")
    font_label.pack(side=tk.LEFT, padx=5)

    font_combo = ctk.CTkOptionMenu(
        formatting_frame, 
        variable=app.current_font,
        values=FONTS,
        command=lambda font_name: app.apply_font(font_name=font_name)
    )
    font_combo.pack(side=tk.LEFT, padx=5)

    # Font size selector
    size_label = ctk.CTkLabel(formatting_frame, text="Size:")
    size_label.pack(side=tk.LEFT, padx=5)

    size_combo = ctk.CTkOptionMenu(
        formatting_frame,
        variable=app.current_font_size,
        values=FONT_SIZES,
        command=lambda font_size: app.apply_font(font_size=font_size)
    )
    size_combo.pack(side=tk.LEFT, padx=5)

    create_separator(formatting_frame)

    # Create formatting toolbar buttons
    for btn_id, btn_data in TOOLBAR_BUTTONS['formatting'].items():
        if btn_id == 'separator':
            create_separator(formatting_frame)
            continue

        command = None
        if btn_id == 'bold':
            command = lambda: toggle_text_property(app.text_area, 'bold')
        elif btn_id == 'italic':
            command = lambda: toggle_text_property(app.text_area, 'italic')
        elif btn_id == 'underline':
            command = lambda: toggle_text_property(app.text_area, 'underline')

        create_toolbar_button(formatting_frame, btn_id, btn_data['tooltip'], command)

    return standard_frame, formatting_frame

def create_separator(parent):
    """Create a toolbar separator"""
    separator = ctk.CTkFrame(parent, width=1, height=20)
    separator.pack(side=tk.LEFT, padx=5, pady=5)

def create_toolbar_button(parent, btn_id, tooltip, command):
    """Create a toolbar button"""
    icon = get_toolbar_icon(btn_id)

    button = ctk.CTkButton(
        parent,
        text="",
        image=icon,
        width=28,
        height=28,
        command=command,
    )
    button.pack(side=tk.LEFT, padx=2)

    # Add tooltip
    create_tooltip(button, tooltip)

    return button

def create_text_area(parent, app):
    """Create the main text editing area"""
    # Create a frame with scrollbars
    text_frame = ctk.CTkFrame(parent)
    text_frame.pack(fill=tk.BOTH, expand=True)

    # Create vertical scrollbar
    scrollbar_y = ctk.CTkScrollbar(text_frame)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Create horizontal scrollbar
    scrollbar_x = ctk.CTkScrollbar(text_frame, orientation=tk.HORIZONTAL)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # We need to use a standard tk.Text widget inside CTkFrame for proper tag support
    # Create text widget
    text_area = tk.Text(
        text_frame,
        wrap="none",
        undo=True,
        xscrollcommand=scrollbar_x.set,
        yscrollcommand=scrollbar_y.set,
        font=("Tahoma", 14),
        bg=COLOR_SCHEME['light']['editor_bg'],
        fg=COLOR_SCHEME['light']['editor_fg'],
        insertbackground=COLOR_SCHEME['light']['editor_fg']
    )
    text_area.pack(fill=tk.BOTH, expand=True)

    # Configure scrollbars
    scrollbar_y.configure(command=text_area.yview)
    scrollbar_x.configure(command=text_area.xview)

    # Configure text tags
    text_area.tag_configure("misspelled", underline=True, underlinefg="red")

    return text_area

def create_suggestion_popup(root, suggestions, callback, x, y):
    """Create a suggestion popup window"""
    popup = tk.Toplevel(root)
    popup.wm_overrideredirect(True)
    popup.wm_geometry(f"+{x}+{y}")

    # Set background color based on theme
    bg_color = COLOR_SCHEME['dark']['suggestion_bg'] if root._get_appearance_mode().lower() == 'dark' else COLOR_SCHEME['light']['suggestion_bg']
    fg_color = COLOR_SCHEME['dark']['suggestion_fg'] if root._get_appearance_mode().lower() == 'dark' else COLOR_SCHEME['light']['suggestion_fg']
    accent_color = "#6699cc"  # Light blue for the number part

    popup.configure(bg=bg_color)

    # Create a frame to hold the suggestions
    frame = tk.Frame(popup, bg=bg_color, bd=1, relief=tk.SOLID)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create labels for each suggestion
    for i, suggestion in enumerate(suggestions[:9]):  # Limit to 9 suggestions
        # Create a container frame for each suggestion row
        row_frame = tk.Frame(frame, bg=bg_color)
        row_frame.pack(fill=tk.X)

        # Create number label (1-9)
        num_label = tk.Label(
            row_frame,
            text=f"{i+1}.",
            font=("Tahoma", 9, "bold"),
            width=2,
            bg=bg_color,
            fg=accent_color,
            padx=2,
            pady=3,
            anchor='w'
        )
        num_label.pack(side=tk.LEFT)

        # Create suggestion text label
        sugg_label = tk.Label(
            row_frame,
            text=f"{suggestion}",
            bg=bg_color,
            fg=fg_color,
            padx=2,
            pady=3,
            anchor='w',
            justify=tk.LEFT
        )
        sugg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bind click event to all elements
        for label in [row_frame, num_label, sugg_label]:
            label.bind("<Button-1>", lambda e, idx=i: (callback(idx), popup.destroy()))
    
    # Bind number keys (1-9) for keyboard selection
    def on_key(event):
        # Check if the key is a number 1-9
        try:
            num = int(event.char)
            if 1 <= num <= len(suggestions) and num <= 9:
                callback(num-1)  # Adjust for 0-based index
                popup.destroy()
        except (ValueError, TypeError):
            pass  # Not a valid number key
        
    # Bind key press event to the root window
    root.bind('<Key>', on_key)
    
    # Unbind key press event when popup is destroyed
    popup.bind("<Destroy>", lambda e: root.unbind('<Key>'))

    return popup

def create_status_bar(parent, app):
    """Create the status bar at the bottom of the window"""
    status_frame = ctk.CTkFrame(parent)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)

    # Position indicator (line, column)
    position_label = ctk.CTkLabel(status_frame, text="Ln 1, Col 1")
    position_label.pack(side=tk.RIGHT, padx=10)

    # Word count
    word_count_label = ctk.CTkLabel(status_frame, text="Words: 0")
    word_count_label.pack(side=tk.LEFT, padx=10)

    # Input method indicator
    input_method_label = ctk.CTkLabel(status_frame, text="Singlish")
    input_method_label.pack(side=tk.LEFT, padx=10)

    # Create a status bar object to hold the widgets
    class StatusBar:
        def __init__(self, frame, position_label, word_count_label, input_method_label):
            self.frame = frame
            self.position_label = position_label
            self.word_count_label = word_count_label
            self.input_method_label = input_method_label

    return StatusBar(status_frame, position_label, word_count_label, input_method_label)

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    def enter(event):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25

        # Create tooltip window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tooltip, 
            text=text, 
            bg="#FFFFE0", 
            relief=tk.SOLID, 
            borderwidth=1,
            padx=2,
            pady=2
        )
        label.pack()

        widget.tooltip = tooltip

    def leave(event):
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def toggle_text_property(text_widget, property_name):
    """Toggle text property (bold, italic, underline) for selected text"""
    try:
        # Get selected text indices
        sel_ranges = text_widget.tag_ranges(tk.SEL)
        if not sel_ranges:
            return  # No selection

        sel_start, sel_end = sel_ranges

        # Get current tags
        current_tags = text_widget.tag_names(sel_start)

        # Parse the current font for proper font properties
        def parse_current_font(widget):
            current_font = widget["font"]
            font_family = "TkDefaultFont"
            font_size = 12  # Default fallback
            
            try:
                if isinstance(current_font, str):
                    # Handle string representation like "Arial 12"
                    parts = current_font.split()
                    if len(parts) >= 2:
                        font_family = parts[0]
                        try:
                            font_size = int(parts[-1])
                        except ValueError:
                            pass  # Keep default
                elif isinstance(current_font, (list, tuple)) and len(current_font) >= 2:
                    # Handle tuple/list like ("Arial", 12)
                    font_family = current_font[0]
                    try:
                        font_size = int(current_font[1])
                    except (ValueError, TypeError):
                        pass  # Keep default
            except Exception as e:
                print(f"Font parsing error: {e}")
                
            return font_family, font_size

        # Define the text properties for each style
        if property_name == "bold":
            # Configure or create the bold tag
            if "bold" not in text_widget.tag_names():
                font_family, font_size = parse_current_font(text_widget)
                import tkinter.font as tkfont
                bold_font = tkfont.Font(family=font_family, size=font_size, weight="bold")
                text_widget.tag_configure("bold", font=bold_font)

        elif property_name == "italic":
            # Configure or create the italic tag
            if "italic" not in text_widget.tag_names():
                font_family, font_size = parse_current_font(text_widget)
                import tkinter.font as tkfont
                italic_font = tkfont.Font(family=font_family, size=font_size, slant="italic")
                text_widget.tag_configure("italic", font=italic_font)

        elif property_name == "underline":
            # Configure or create the underline tag
            if "underline" not in text_widget.tag_names():
                text_widget.tag_configure("underline", underline=True)

        # Check if tag exists on selection
        if property_name in current_tags:
            # Remove the tag
            text_widget.tag_remove(property_name, sel_start, sel_end)
        else:
            # Add the tag
            text_widget.tag_add(property_name, sel_start, sel_end)
    except Exception as e:
        print(f"Error in toggle_text_property: {e}")
        # No selection or other error, do nothing
        pass