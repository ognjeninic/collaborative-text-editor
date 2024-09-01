import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Collaborative Text Editor")
        self.root.geometry("800x600")

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
        
        # Edit menu
        edit_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)
        
        # Format menu
        format_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=self.make_bold)
        format_menu.add_command(label="Italic", command=self.make_italic)
        format_menu.add_command(label="Underline", command=self.make_underline)
        format_menu.add_command(label="Text Color", command=self.change_text_color)
        
        # Alignment menu
        alignment_menu = tk.Menu(format_menu, tearoff=False)
        format_menu.add_cascade(label="Align", menu=alignment_menu)
        alignment_menu.add_command(label="Left", command=self.align_left)
        alignment_menu.add_command(label="Center", command=self.align_center)
        alignment_menu.add_command(label="Right", command=self.align_right)
        alignment_menu.add_command(label="Justify", command=self.align_justify)

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
        for size in range(8, 33, 2):
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

    def make_bold(self):
        bold_font = font.Font(self.text_area, self.text_area.cget("font"))
        bold_font.configure(weight="bold")
        self.text_area.tag_configure("bold", font=bold_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("bold", "sel.first", "sel.last")

    def make_italic(self):
        italic_font = font.Font(self.text_area, self.text_area.cget("font"))
        italic_font.configure(slant="italic")
        self.text_area.tag_configure("italic", font=italic_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("italic", "sel.first", "sel.last")

    def make_underline(self):
        underline_font = font.Font(self.text_area, self.text_area.cget("font"))
        underline_font.configure(underline=True)
        self.text_area.tag_configure("underline", font=underline_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("underline", "sel.first", "sel.last")

    def align_left(self):
        """Align the selected text to the left."""
        self.text_area.tag_configure("left", justify='left')
        self.text_area.tag_add("left", "sel.first", "sel.last")

    def align_center(self):
        """Center the selected text."""
        self.text_area.tag_configure("center", justify='center')
        self.text_area.tag_add("center", "sel.first", "sel.last")

    def align_right(self):
        """Align the selected text to the right."""
        self.text_area.tag_configure("right", justify='right')
        self.text_area.tag_add("right", "sel.first", "sel.last")

    def align_justify(self):
        """Justify the selected text."""
        self.text_area.tag_configure("justify", justify='justify')
        self.text_area.tag_add("justify", "sel.first", "sel.last")


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()