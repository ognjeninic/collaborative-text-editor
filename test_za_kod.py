import tkinter as tk
from tkinter import filedialog, font, colorchooser, messagebox
import os

class TextEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Collaborative Editor")
        self.root.geometry("1200x800")

        # Initial setup for the home page and text area
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)
        self.text_area = None

        # Current file tracking
        self.current_file = None

        # Display the home page
        self.home_page()

    def home_page(self):
        """Display the home page with a list of text files to open and edit."""
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.file_list_frame = tk.Frame(self.main_frame)
        self.file_list_frame.pack(fill='both', expand=True)

        self.refresh_file_list()

        refresh_button = tk.Button(self.file_list_frame, text="Refresh", command=self.refresh_file_list)
        refresh_button.pack(side='bottom', pady=10)

    def refresh_file_list(self):
        """Refresh the list of text files displayed on the home page."""
        # Clear current list
        for widget in self.file_list_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        # Get list of text files from the current directory
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]

        for file in files:
            file_button = tk.Button(self.file_list_frame, text=file, command=lambda f=file: self.open_file(f))
            file_button.pack(fill='x', padx=10, pady=5)

    def open_file(self, filename=None):
        """Open a text file for editing."""
        self.current_file = filename

        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create text area for editing
        self.text_area = tk.Text(self.main_frame, wrap='word', undo=True, font=("Arial", 12))
        self.text_area.pack(fill='both', expand=True)

        # Create a menu bar
        self.create_menu()

        # Load the file content into the text area if editing an existing file
        if self.current_file:
            with open(self.current_file, "r") as file:
                self.text_area.insert(1.0, file.read())

    def create_menu(self):
        """Create the menu bar for the text editor."""
        self.main_menu = tk.Menu(self.root)
        self.root.config(menu=self.main_menu)

        # File menu
        file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)

        # Format menu
        format_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=self.make_bold)
        format_menu.add_command(label="Italic", command=self.make_italic)
        format_menu.add_command(label="Underline", command=self.make_underline)
        format_menu.add_separator()
        format_menu.add_command(label="Text Color", command=self.change_text_color)

        # Font menu
        font_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Font", menu=font_menu)

        # Font Family
        self.font_var = tk.StringVar(value="Arial")
        font_families = sorted(font.families())
        font_menu.add_cascade(label="Font Family", menu=self.create_font_family_menu(font_families))

        # Font Size
        self.font_size_var = tk.StringVar(value="12")
        font_menu.add_cascade(label="Font Size", menu=self.create_font_size_menu())

    def create_font_family_menu(self, font_families):
        """Create the font family menu."""
        font_family_menu = tk.Menu(self.main_menu, tearoff=False)
        for family in font_families:
            font_family_menu.add_radiobutton(label=family, variable=self.font_var, command=self.apply_font)
        return font_family_menu

    def create_font_size_menu(self):
        """Create the font size menu."""
        font_size_menu = tk.Menu(self.main_menu, tearoff=False)
        for size in range(8, 72, 2):
            font_size_menu.add_radiobutton(label=str(size), variable=self.font_size_var, command=self.apply_font)
        return font_size_menu

    def apply_font(self):
        """Apply the selected font family and size to the selected text."""
        selected_font = font.Font(family=self.font_var.get(), size=self.font_size_var.get())
        self.text_area.tag_configure("selected_font", font=selected_font)
        
        current_tags = self.text_area.tag_names("sel.first")
        if "selected_font" in current_tags:
            self.text_area.tag_remove("selected_font", "sel.first", "sel.last")
        self.text_area.tag_add("selected_font", "sel.first", "sel.last")

    def change_text_color(self):
        """Change the color of the selected text."""
        color = colorchooser.askcolor()[1]
        if color:
            self.text_area.tag_configure("color", foreground=color)
            current_tags = self.text_area.tag_names("sel.first")
            if "color" in current_tags:
                self.text_area.tag_remove("color", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("color", "sel.first", "sel.last")

    def cut_text(self):
        """Cut the selected text."""
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        """Copy the selected text."""
        selected_text = self.text_area.get("sel.first", "sel.last")
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def paste_text(self):
        """Paste the text from the clipboard."""
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass

    def new_file(self):
        """Create a new text file."""
        self.text_area.delete(1.0, tk.END)
        self.current_file = None

    def save_file(self):
        """Save the current text file."""
        if self.current_file:
            content = self.text_area.get(1.0, tk.END)
            with open(self.current_file, "w") as file:
                file.write(content)
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save the text file with a new name."""
        self.current_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                         filetypes=[("Text Files", "*.txt"),
                                                                    ("All Files", "*.*")])
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))

    def make_bold(self):
        """Make the selected text bold."""
        bold_font = font.Font(self.text_area, self.text_area.cget("font"))
        bold_font.configure(weight="bold")
        self.text_area.tag_configure("bold", font=bold_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("bold", "sel.first", "sel.last")

    def make_italic(self):
        """Make the selected text italic."""
        italic_font = font.Font(self.text_area, self.text_area.cget("font"))
        italic_font.configure(slant="italic")
        self.text_area.tag_configure("italic", font=italic_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("italic", "sel.first", "sel.last")

    def make_underline(self):
        """Underline the selected text."""
        underline_font = font.Font(self.text_area, self.text_area.cget("font"))
        underline_font.configure(underline=True)
        self.text_area.tag_configure("underline", font=underline_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("underline", "sel.first", "sel.last")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditorApp(root)
    root.mainloop()