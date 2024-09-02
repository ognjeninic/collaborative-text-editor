import tkinter as tk
from tkinter import filedialog, font, colorchooser
from PIL import Image, ImageTk

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
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_command(label="Insert Image", command=self.insert_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Clipboard menu
        edit_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Clipboard", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Paste", command=self.paste_text)
        
        # Edit menu
        edit_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo_action)
        edit_menu.add_command(label="Redo", command=self.redo_action)

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

        self.current_file = None

    def create_font_family_menu(self, font_families):
        font_family_menu = tk.Menu(self.main_menu, tearoff=False)
        for family in font_families:
            font_family_menu.add_radiobutton(label=family, variable=self.font_var, command=self.apply_font)
        return font_family_menu

    def create_font_size_menu(self):
        font_size_menu = tk.Menu(self.main_menu, tearoff=False)
        for size in range(8, 72, 2):
            font_size_menu.add_radiobutton(label=str(size), variable=self.font_size_var, command=self.apply_font)
        return font_size_menu

    def apply_font(self):
        selected_font = font.Font(family=self.font_var.get(), size=self.font_size_var.get())
        tag_name = f"font_{self.font_var.get()}_{self.font_size_var.get()}"

        self.text_area.tag_configure(tag_name, font=selected_font)

        try:
            self.text_area.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass  # Ignore if no text is selected

    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            tag_name = f"color_{color}"
            self.text_area.tag_configure(tag_name, foreground=color)
            try:
                self.text_area.tag_add(tag_name, "sel.first", "sel.last")
            except tk.TclError:
                pass

    def cut_text(self):
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        try:
            selected_text = self.text_area.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass

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

    def undo_action(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass  # No more undo steps available

    def redo_action(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass  # No more redo steps available

    def make_bold(self):
        self.apply_tag("bold", weight="bold")

    def make_italic(self):
        self.apply_tag("italic", slant="italic")

    def make_underline(self):
        self.apply_tag("underline", underline=True)

    def apply_tag(self, tag_name, **options):
        font_style = font.Font(self.text_area, self.text_area.cget("font"))
        font_style.configure(**options)
        self.text_area.tag_configure(tag_name, font=font_style)

        try:
            current_tags = self.text_area.tag_names("sel.first")
            if tag_name in current_tags:
                self.text_area.tag_remove(tag_name, "sel.first", "sel.last")
            else:
                self.text_area.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass  # No selection

    def insert_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All Files", "*.*")])
        if image_path:
            image = Image.open(image_path)
            image.thumbnail((300, 300))  # Adjust size as needed
            img = ImageTk.PhotoImage(image)
            self.text_area.image_create(tk.END, image=img)
            self.text_area.image = img  # Prevent garbage collection of the image


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
