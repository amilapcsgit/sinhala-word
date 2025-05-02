import tkinter as tk
import customtkinter as ctk
from config import COLOR_SCHEME

class ThemeManager:
    """
    Manages the application theme (dark/light mode)
    """
    def __init__(self, root):
        self.root = root
        self.current_theme = "light"  # Default theme
        
        # Apply initial theme
        self.apply_theme()
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        # Set appearance mode for customtkinter
        ctk.set_appearance_mode(self.current_theme)
        
        # Get color scheme for current theme
        colors = COLOR_SCHEME[self.current_theme]
        
        # Apply colors to root window
        self.root.configure(fg_color=colors['window_bg'])
        
        # Update all child widgets that need theme-specific settings
        # This will be called after the UI is created
        self.update_widgets_theme()
    
    def update_widgets_theme(self):
        """Update theme for all widgets in the application"""
        # This method is called after UI initialization and when theme changes
        try:
            # Get application instance
            app = getattr(self.root, '_app', None)
            if not app:
                return
                
            # Get colors for the current theme
            colors = COLOR_SCHEME[self.current_theme]
            
            # Text area specific settings
            if hasattr(app, 'text_area'):
                app.text_area.configure(
                    bg=colors['editor_bg'],
                    fg=colors['editor_fg'],
                    insertbackground=colors['editor_fg']
                )
                
                # Update text tags for the current theme
                app.text_area.tag_configure("misspelled", underline=True, underlinefg="red")
                
        except (AttributeError, tk.TclError):
            # UI might not be fully initialized yet
            pass
