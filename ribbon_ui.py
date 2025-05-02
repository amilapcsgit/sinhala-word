import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from icons import get_toolbar_icon
from config import COLOR_SCHEME

class RibbonButton(ctk.CTkButton):
    """Enhanced button with icon and text for ribbon UI"""
    
    def __init__(self, parent, icon_name, text, command=None, tooltip=None, **kwargs):
        # Get the icon
        self.icon = get_toolbar_icon(icon_name)
        
        # Create the button with both icon and text
        super().__init__(
            parent,
            text=text,
            image=self.icon,
            compound=tk.TOP,  # Icon above text
            command=command,
            width=60,
            height=60,
            corner_radius=6,
            **kwargs
        )
        
        # Add tooltip if provided
        if tooltip:
            self.tooltip_text = tooltip
            self.bind("<Enter>", self._show_tooltip)
            self.bind("<Leave>", self._hide_tooltip)
            self.tooltip = None
    
    def _show_tooltip(self, event):
        """Show tooltip when mouse enters the button"""
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + 25
        y += self.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Get theme-specific colors
        if self._get_appearance_mode().lower() == 'dark':
            bg_color = COLOR_SCHEME['dark']['tooltip_bg'] if 'tooltip_bg' in COLOR_SCHEME['dark'] else "#333333"
            fg_color = COLOR_SCHEME['dark']['tooltip_fg'] if 'tooltip_fg' in COLOR_SCHEME['dark'] else "#ffffff"
        else:
            bg_color = COLOR_SCHEME['light']['tooltip_bg'] if 'tooltip_bg' in COLOR_SCHEME['light'] else "#FFFFE0"
            fg_color = COLOR_SCHEME['light']['tooltip_fg'] if 'tooltip_fg' in COLOR_SCHEME['light'] else "#000000"
        
        label = tk.Label(
            self.tooltip, 
            text=self.tooltip_text, 
            bg=bg_color, 
            fg=fg_color,
            relief=tk.SOLID, 
            borderwidth=1,
            padx=4,
            pady=2
        )
        label.pack()
    
    def _hide_tooltip(self, event):
        """Hide tooltip when mouse leaves the button"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class RibbonTab(ctk.CTkFrame):
    """A tab in the ribbon interface"""
    
    def __init__(self, parent, name, **kwargs):
        super().__init__(parent, **kwargs)
        self.name = name
        self.sections = {}
    
    def add_section(self, name):
        """Add a new section to the tab"""
        section = RibbonSection(self, name)
        self.sections[name] = section
        section.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        return section

class RibbonSection(ctk.CTkFrame):
    """A section within a ribbon tab"""
    
    def __init__(self, parent, name, **kwargs):
        super().__init__(parent, **kwargs)
        self.name = name
        
        # Create a frame for the buttons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Add section label at the bottom
        self.label = ctk.CTkLabel(self, text=name, font=("Segoe UI", 10))
        self.label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def add_button(self, icon_name, text, command=None, tooltip=None, **kwargs):
        """Add a button to the section"""
        button = RibbonButton(
            self.button_frame,
            icon_name=icon_name,
            text=text,
            command=command,
            tooltip=tooltip,
            **kwargs
        )
        button.pack(side=tk.LEFT, padx=2, pady=2)
        return button
    
    def add_separator(self):
        """Add a vertical separator to the section"""
        separator = ctk.CTkFrame(self.button_frame, width=1)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        return separator

class Ribbon(ctk.CTkFrame):
    """Main ribbon interface"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create tab buttons frame
        self.tab_buttons_frame = ctk.CTkFrame(self)
        self.tab_buttons_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Create tab content frame
        self.tab_content_frame = ctk.CTkFrame(self)
        self.tab_content_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        self.tabs = {}
        self.tab_buttons = {}
        self.active_tab = None
    
    def add_tab(self, name):
        """Add a new tab to the ribbon"""
        # Create tab button
        button = ctk.CTkButton(
            self.tab_buttons_frame,
            text=name,
            corner_radius=0,
            height=30,
            command=lambda: self.activate_tab(name)
        )
        button.pack(side=tk.LEFT, padx=1, pady=0)
        self.tab_buttons[name] = button
        
        # Create tab content
        tab = RibbonTab(self.tab_content_frame, name)
        self.tabs[name] = tab
        
        # If this is the first tab, activate it
        if not self.active_tab:
            self.activate_tab(name)
        
        return tab
    
    def activate_tab(self, name):
        """Activate the specified tab"""
        # Hide all tabs
        for tab_name, tab in self.tabs.items():
            tab.pack_forget()
            
            # Update button appearance
            if tab_name == name:
                self.tab_buttons[tab_name].configure(fg_color=self.tab_buttons[tab_name]._fg_color)
            else:
                self.tab_buttons[tab_name].configure(fg_color=self.tab_buttons[tab_name]._bg_color)
        
        # Show the selected tab
        self.tabs[name].pack(fill=tk.BOTH, expand=True)
        self.active_tab = name

def create_ribbon_ui(parent, app):
    """Create a ribbon UI for the application"""
    # Create main ribbon
    ribbon = Ribbon(parent)
    ribbon.pack(fill=tk.X, side=tk.TOP)
    
    # Create File tab
    file_tab = ribbon.add_tab("File")
    
    # Document section
    document_section = file_tab.add_section("Document")
    document_section.add_button("new", "New", command=app.new_file, tooltip="Create a new document")
    document_section.add_button("open", "Open", command=app.open_file, tooltip="Open an existing document")
    document_section.add_button("save", "Save", command=app.save_file, tooltip="Save the current document")
    
    # Edit section
    edit_section = file_tab.add_section("Edit")
    edit_section.add_button("cut", "Cut", 
                           command=lambda: app.text_area.event_generate("<<Cut>>"),
                           tooltip="Cut the selected text")
    edit_section.add_button("copy", "Copy", 
                           command=lambda: app.text_area.event_generate("<<Copy>>"),
                           tooltip="Copy the selected text")
    edit_section.add_button("paste", "Paste", 
                           command=lambda: app.text_area.event_generate("<<Paste>>"),
                           tooltip="Paste text from clipboard")
    
    # History section
    history_section = file_tab.add_section("History")
    history_section.add_button("undo", "Undo", 
                              command=lambda: app.text_area.event_generate("<<Undo>>"),
                              tooltip="Undo the last action")
    history_section.add_button("redo", "Redo", 
                              command=lambda: app.text_area.event_generate("<<Redo>>"),
                              tooltip="Redo the last undone action")
    
    # Create Format tab
    format_tab = ribbon.add_tab("Format")
    
    # Font section
    font_section = format_tab.add_section("Font")
    font_section.add_button("bold", "Bold", 
                           command=lambda: toggle_text_property(app.text_area, 'bold'),
                           tooltip="Make text bold")
    font_section.add_button("italic", "Italic", 
                           command=lambda: toggle_text_property(app.text_area, 'italic'),
                           tooltip="Make text italic")
    font_section.add_button("underline", "Underline", 
                           command=lambda: toggle_text_property(app.text_area, 'underline'),
                           tooltip="Underline text")
    
    # Alignment section
    alignment_section = format_tab.add_section("Alignment")
    alignment_section.add_button("align_left", "Left", 
                                tooltip="Align text to the left")
    alignment_section.add_button("align_center", "Center", 
                                tooltip="Center text")
    alignment_section.add_button("align_right", "Right", 
                                tooltip="Align text to the right")
    
    # Create View tab
    view_tab = ribbon.add_tab("View")
    
    # Theme section
    theme_section = view_tab.add_section("Theme")
    theme_section.add_button("theme", "Toggle\nTheme", 
                            command=app.toggle_theme,
                            tooltip="Switch between light and dark theme")
    
    # Input section
    input_section = view_tab.add_section("Input")
    input_section.add_button("keyboard", "Sinhala\nKeyboard", 
                            command=app.toggle_keyboard,
                            tooltip="Show/hide the Sinhala keyboard")
    
    return ribbon

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
        
        # Check if the property is already applied
        if property_name in current_tags:
            # Remove the property
            text_widget.tag_remove(property_name, sel_start, sel_end)
        else:
            # Apply the property
            text_widget.tag_add(property_name, sel_start, sel_end)
            
            # Configure the tag if it doesn't exist yet
            if property_name == "bold":
                text_widget.tag_configure("bold", font=("Tahoma", 12, "bold"))
            elif property_name == "italic":
                text_widget.tag_configure("italic", font=("Tahoma", 12, "italic"))
            elif property_name == "underline":
                text_widget.tag_configure("underline", underline=True)
                
    except (tk.TclError, IndexError):
        # No selection or other error
        pass