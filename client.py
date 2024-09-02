import tkinter as tk
from tkinter import filedialog, font, colorchooser, simpledialog
from PIL import Image, ImageTk
import webbrowser

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Collaborative Word")
        self.root.geometry("1920x1080")

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
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)

        # Format menu
        format_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=self.make_bold)
        format_menu.add_command(label="Italic", command=self.make_italic)
        format_menu.add_command(label="Underline", command=self.make_underline)
        format_menu.add_separator()
        format_menu.add_command(label="Insert Hyperlink", command=self.insert_hyperlink_with_hover)
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
            pass

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

    def make_bold(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "italic" in current_tags and "underline" in current_tags:
            self.make_bolditalicunderline()
        elif "italic" in current_tags:
            self.make_bolditalic()
        elif "underline" in current_tags:
            self.make_boldunderline()
        else:
            bold_font = font.Font(self.text_area, self.text_area.cget("font"))
            bold_font.configure(weight="bold")
            self.text_area.tag_configure("bold", font=bold_font)

            if "bold" in current_tags:
                self.text_area.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("bold", "sel.first", "sel.last")

    def make_italic(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "bold" in current_tags and "underline" in current_tags:
            self.make_bolditalicunderline()
        elif "bold" in current_tags:
            self.make_bolditalic()
        elif "underline" in current_tags:
            self.make_italicunderline()
        else:
            italic_font = font.Font(self.text_area, self.text_area.cget("font"))
            italic_font.configure(slant="italic")
            self.text_area.tag_configure("italic", font=italic_font)

            if "italic" in current_tags:
                self.text_area.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("italic", "sel.first", "sel.last")

    def make_underline(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "bolditalic" in current_tags:
            self.make_bolditalicunderline()
        elif "bold" in current_tags:
            self.make_boldunderline()
        elif "italic" in current_tags:
            self.make_italicunderline()
        else:
            underline_font = font.Font(self.text_area, self.text_area.cget("font"))
            underline_font.configure(underline=True)
            self.text_area.tag_configure("underline", font=underline_font)

            if "underline" in current_tags:
                self.text_area.tag_remove("underline", "sel.first", "sel.last")
            else:
                self.text_area.tag_add("underline", "sel.first", "sel.last")

    def make_bolditalic(self):
        bolditalic_font = font.Font(self.text_area, self.text_area.cget("font"))
        bolditalic_font.configure(weight="bold", slant="italic")
        self.text_area.tag_configure("bolditalic", font=bolditalic_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "bolditalic" in current_tags:
            self.text_area.tag_remove("bolditalic", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("bolditalic", "sel.first", "sel.last")

        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")

    def make_boldunderline(self):
        boldunderline_font = font.Font(self.text_area, self.text_area.cget("font"))
        boldunderline_font.configure(weight="bold", underline=True)
        self.text_area.tag_configure("boldunderline", font=boldunderline_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "boldunderline" in current_tags:
            self.text_area.tag_remove("boldunderline", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("boldunderline", "sel.first", "sel.last")

        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")

    def make_italicunderline(self):
        italicunderline_font = font.Font(self.text_area, self.text_area.cget("font"))
        italicunderline_font.configure(slant="italic", underline=True)
        self.text_area.tag_configure("italicunderline", font=italicunderline_font)

        current_tags = self.text_area.tag_names("sel.first")
        if "italicunderline" in current_tags:
            self.text_area.tag_remove("italicunderline", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("italicunderline", "sel.first", "sel.last")

        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")

    def make_bolditalicunderline(self):
        bolditalicunderline_font = font.Font(self.text_area, self.text_area.cget("font"))
        bolditalicunderline_font.configure(weight="bold", slant="italic", underline=True)
        self.text_area.tag_configure("bolditalicunderline", font=bolditalicunderline_font)
        current_tags = self.text_area.tag_names("sel.first")
        if "bolditalicunderline" in current_tags:
            self.text_area.tag_remove("bolditalicunderline", "sel.first", "sel.last")
        else:
            self.text_area.tag_add("bolditalicunderline", "sel.first", "sel.last")

        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")

    def insert_hyperlink_with_hover(self):
        url = simpledialog.askstring("Insert Hyperlink", "Enter URL:")
        if url:
            display_text = simpledialog.askstring("Insert Hyperlink", "Enter the display text:")
            if not display_text:
                display_text = url  

        link = self.hyperlink(self.root, url, text=display_text)
        self.text_area.window_create(tk.INSERT, window=link)


    def hyperlink(self, root, link: str, **kwargs) -> tk.Label:
        
        for i in (("fg", "magenta"), ("text", "Hyperlink!"), ("font", "None 10"), ("cursor", "hand2")):
            kwargs.setdefault(i[0], i[1])

        
        label = tk.Label(root, **kwargs)
        label.link = link

        
        label.bind("<Button-1>", lambda e: webbrowser.open(e.widget.link))
        label.bind("<Enter>", lambda e: e.widget.configure(font=e.widget.cget("font") + " underline"))
        label.bind("<Leave>", lambda e: e.widget.configure(font=e.widget.cget("font")[:-10]))

        return label

    def insert_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            image = Image.open(file_path)
            image.thumbnail((300, 300))
            self.image = ImageTk.PhotoImage(image)
            self.text_area.image_create(tk.INSERT, image=self.image)

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
