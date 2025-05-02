import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pyside_keyboard import SinhalaKeyboard
from theme_manager import ThemeManager
from transliterator import SinhalaTransliterator
from ui_components import create_menu, create_text_area, create_status_bar, create_suggestion_popup
from ribbon_ui import create_ribbon_ui


class SinhalaWordProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("SinhalaSage")
        self.root.geometry("1024x768")
        self.current_file = None
        self.is_modified = False
        self.current_font = tk.StringVar(value="Arial")
        self.current_font_size = tk.StringVar(value="12")
        self.keyboard_visible = False
        self.current_word = ""
        self.suggestion_popup = None
        
        # Initialize transliterator
        with open('sinhalawordmap.json', 'r', encoding='utf-8') as file:
            self.word_map = json.load(file)
        self.transliterator = SinhalaTransliterator(self.word_map)

        # Initialize window protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle closing event
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(self.root)
        
        # Initialize all UI frames first
        self.ribbon_frame = ctk.CTkFrame(self.root)
        self.text_frame = ctk.CTkFrame(self.root)
        
        # Create all UI components
        create_menu(self.root, self)
        
        # Pack and create ribbon UI
        self.ribbon_frame.pack(fill=tk.X, side=tk.TOP)
        self.ribbon = create_ribbon_ui(self.ribbon_frame, self)
        
        # Pack and create text area
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        self.text_area = create_text_area(self.text_frame, self)
        
        # Create status bar
        self.status_bar = create_status_bar(self.root, self)

        # Initialize keyboard as additional input method
        # Use PySide6 keyboard with dark mode support
        self.keyboard = SinhalaKeyboard(parent=None, dark_mode=self.theme_manager.current_theme == "dark")
        self.keyboard.hide()  # Hide initially
        self.keyboard_visible = False
        
        # Connect keyboard signal to our insert_text method
        self.keyboard.keyPressed.connect(self.insert_text)

        # Bind text input events
        self.text_area.bind('<Key>', self.on_key_press)
        self.text_area.bind('<space>', self.on_space)
        self.text_area.bind('<Return>', self.on_return)

    # Method removed as its functionality was already in __init__



    def new_file(self):
        """Create a new file"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Save Changes?",
                "Do you want to save changes before creating a new file?"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()

        # Clear text area
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.is_modified = False
        self.update_ui()

    def open_file(self):
        """Open a file"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Save Changes?",
                "Do you want to save changes before opening a new file?"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()

        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.current_file = file_path
                self.is_modified = False
                self.update_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {str(e)}")

    def save_file(self):
        """Save current file"""
        if not self.current_file:
            return self.save_as_file()

        try:
            content = self.text_area.get("1.0", tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            self.is_modified = False
            self.update_ui()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {str(e)}")
            return False

    def save_as_file(self):
        """Save file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            self.current_file = file_path
            return self.save_file()

        return False

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_manager.toggle_theme()
        
        # Update keyboard theme
        is_dark = self.theme_manager.current_theme == "dark"
        self.keyboard.set_dark_mode(is_dark)

    def toggle_toolbars(self):
        """Toggle visibility of ribbon UI"""
        if self.ribbon_frame.winfo_viewable():
            self.ribbon_frame.pack_forget()
        else:
            self.ribbon_frame.pack(fill=tk.X, side=tk.TOP)
            # Re-order to ensure correct placement
            self.text_frame.pack_forget()
            self.text_frame.pack(fill=tk.BOTH, expand=True)
            self.status_bar.frame.pack_forget()
            self.status_bar.frame.pack(fill=tk.X, side=tk.BOTTOM)

    def apply_font(self, font_name=None, font_size=None):
        """Apply selected font to text"""
        if font_name:
            self.current_font.set(font_name)

        if font_size:
            self.current_font_size.set(font_size)

        # Apply to text area
        font_spec = (self.current_font.get(), int(self.current_font_size.get()))
        self.text_area.configure(font=font_spec)

    def on_closing(self):
        """Handle window closing"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Save Changes?",
                "Do you want to save changes before exiting?"
            )
            if result is None:  # Cancel
                return
            elif result:  # Yes
                if not self.save_file():
                    return  # If save was cancelled or failed, don't close

        self.root.destroy()

    def toggle_keyboard(self):
        """Toggle on-screen keyboard"""
        if self.keyboard_visible:
            self.keyboard.hide()
            self.keyboard_visible = False
        else:
            # Show the keyboard as a separate window
            self.keyboard.show()
            self.keyboard_visible = True

    def insert_text(self, char):
        """Insert text from keyboard or handle transliteration"""
        self.text_area.insert(tk.INSERT, char)
        # Don't reset current_word for keyboard input to maintain transliteration state

    def on_key_press(self, event):
        """Handle key press events for transliteration"""
        if event.char and not event.char.isspace():
            self.current_word += event.char
            suggestions = self.transliterator.get_suggestions(self.current_word)
            if suggestions:
                self.show_suggestions(suggestions)

    def on_space(self, event):
        """Handle space and return key events"""
        if self.current_word:
            transliterated = self.transliterator.transliterate(self.current_word)
            if transliterated != self.current_word:
                # Delete the English word
                pos = self.text_area.index(tk.INSERT)
                start_pos = f"{pos} - {len(self.current_word)}c"
                self.text_area.delete(start_pos, pos)
                # Insert transliterated word
                self.text_area.insert(tk.INSERT, transliterated)
            self.current_word = ""
            if self.suggestion_popup:
                self.suggestion_popup.destroy()
                self.suggestion_popup = None
        
        # Add a space after transliteration or when there's no word to transliterate
        self.text_area.insert(tk.INSERT, " ")
        return 'break'

    def show_suggestions(self, suggestions):
        """Show suggestion popup"""
        if self.suggestion_popup:
            self.suggestion_popup.destroy()
        
        x = self.root.winfo_x() + self.text_area.winfo_x() + 50
        y = self.root.winfo_y() + self.text_area.winfo_y() + 50
        
        self.suggestion_popup = create_suggestion_popup(
            self.root,
            suggestions,
            lambda idx: self.use_suggestion(suggestions[idx]),
            x, y
        )

    def use_suggestion(self, suggestion):
        """Use selected suggestion"""
        pos = self.text_area.index(tk.INSERT)
        start_pos = f"{pos} - {len(self.current_word)}c"
        self.text_area.delete(start_pos, pos)
        self.text_area.insert(tk.INSERT, suggestion)
        self.current_word = ""

    def on_return(self, event):
        """Handle return key events"""
        if self.current_word:
            # Handle transliteration like in on_space
            transliterated = self.transliterator.transliterate(self.current_word)
            if transliterated != self.current_word:
                # Delete the English word
                pos = self.text_area.index(tk.INSERT)
                start_pos = f"{pos} - {len(self.current_word)}c"
                self.text_area.delete(start_pos, pos)
                # Insert transliterated word
                self.text_area.insert(tk.INSERT, transliterated)
            self.current_word = ""
            if self.suggestion_popup:
                self.suggestion_popup.destroy()
                self.suggestion_popup = None
            
            # After transliteration, add a newline
            self.text_area.insert(tk.INSERT, "\n")
            return 'break'
        else:
            # No Singlish word to transliterate, allow the normal Enter key behavior
            # to insert a newline by not returning 'break'
            self.text_area.insert(tk.INSERT, "\n")
            return 'break'  # Still use 'break' to ensure consistent behavior

    def update_ui(self):
        """Update UI elements based on file state"""
        # Add any UI updates here (e.g., enable/disable save button)
        pass


def main():
    # Set up customtkinter
    ctk.set_appearance_mode("light")  # Default theme
    ctk.set_default_color_theme("blue")

    # Create root window
    root = ctk.CTk()
    app = SinhalaWordProcessor(root)

    # Store app reference for theme manager
    root._app = app

    # Start application
    root.mainloop()

if __name__ == "__main__":
    main()