import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Collaborative Word")
        self.root.geometry("1980x1080")

        self.text_area = tk.Text(self.root, wrap='word', undo=True)
        self.text_area.pack(fill='both', expand=True)

        self.main_menu = tk.Menu()
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

        # Clipboard menu
        clipboard_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Clipboard", menu=clipboard_menu)
        clipboard_menu.add_command(label="Copy", command=self.copy_text)
        clipboard_menu.add_command(label="Cut", command=self.cut_text)
        clipboard_menu.add_separator()
        clipboard_menu.add_command(label="Paste", command=self.paste_text)
        
        # Edit menu
        edit_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)

        # Format menu
        format_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Format", menu=format_menu)
        format_menu.add_checkbutton(label="Bold", command=self.make_bold)
        format_menu.add_checkbutton(label="Italic", command=self.make_italic)
        format_menu.add_checkbutton(label="Underline", command=self.make_underline)
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

        self.current_font = font.Font(family=self.font_var.get(), size=self.font_size_var.get())
        self.text_area.configure(font=self.current_font)

        self.current_file = None

    def create_font_family_menu(self, font_families):
        font_family_menu = tk.Menu(self.main_menu, tearoff=False)
        for family in font_families:
            font_family_menu.add_radiobutton(label=family, variable=self.font_var, command=self.change_font)
        return font_family_menu

    def create_font_size_menu(self):
        font_size_menu = tk.Menu(self.main_menu, tearoff=False)
        for size in range(8, 72, 2):
            font_size_menu.add_radiobutton(label=str(size), variable=self.font_size_var, command=self.change_font)
        return font_size_menu

    def change_font(self):
        self.current_font.configure(family=self.font_var.get(), size=self.font_size_var.get())
        self.text_area.configure(font=self.current_font)

    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text_area.tag_configure("color", foreground=color)
            current_tags = self.text_area.tag_names("sel.first")
            if "color" in current_tags:
                self.text_area.tag_remove("color", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("color", "sel.first", "sel.last")

    def cut_text(self):
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        selected_text = self.text_area.get("sel.first", "sel.last")
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def paste_text(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None

    def open_file(self):
        self.current_file = filedialog.askopenfilename(defaultextension=".txt",
                                                      filetypes=[("Text Files", "*.txt"),
                                                                 ("All Files", "*.*")])
        if self.current_file:
            with open(self.current_file, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, file.read())

    def save_file(self):
        if self.current_file:
            content = self.text_area.get(1.0, tk.END)
            with open(self.current_file, "w") as file:
                file.write(content)
        else:
            self.save_as_file()

    def save_as_file(self):
        self.current_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                         filetypes=[("Text Files", "*.txt"),
                                                                    ("All Files", "*.*")])
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))

    def apply_tag(self, tag_name, font_config):
        # Configure the font for the tag
        self.text_area.tag_configure(tag_name, font=font_config)

        # Apply or remove the tag from selected text
        current_tags = self.text_area.tag_names("sel.first")
        if tag_name in current_tags:
            self.text_area.tag_remove(tag_name, "sel.first", "sel.last")
        else:
            self.text_area.tag_add(tag_name, "sel.first", "sel.last")

    def make_bold(self):
        bold_font = font.Font(self.text_area, self.text_area.cget("font"))
        bold_font.configure(weight="bold")
        self.apply_tag("bold", bold_font)
        self.update_combined_tags()

    def make_italic(self):
        italic_font = font.Font(self.text_area, self.text_area.cget("font"))
        italic_font.configure(slant="italic")
        self.apply_tag("italic", italic_font)
        self.update_combined_tags()

    def make_underline(self):
        underline_font = font.Font(self.text_area, self.text_area.cget("font"))
        underline_font.configure(underline=True)
        self.apply_tag("underline", underline_font)
        self.update_combined_tags()

    def update_combined_tags(self):
        """Updates the font for combinations of bold, italic, and underline tags."""
        # Create combined styles for bold, italic, and underline
        combined_font = font.Font(self.text_area, self.text_area.cget("font"))
        if "bold" in self.text_area.tag_names("sel.first"):
            combined_font.configure(weight="bold")
        if "italic" in self.text_area.tag_names("sel.first"):
            combined_font.configure(slant="italic")
        if "underline" in self.text_area.tag_names("sel.first"):
            combined_font.configure(underline=True)
        
        # Configure the combined tag
        self.text_area.tag_configure("combined", font=combined_font)
        
        # Apply or remove combined tag
        current_tags = self.text_area.tag_names("sel.first")
        if "combined" in current_tags:
            self.text_area.tag_remove("combined", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("combined", "sel.first", "sel.last")


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()