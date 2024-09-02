import tkinter as tk
from tkinter import filedialog, font, colorchooser, simpledialog, messagebox
from PIL import Image, ImageTk
import webbrowser
import homepage  # Import the homepage script
import os

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Collaborative Word")
        self.root.geometry("1980x1080")

        # Initialize font variables
        self.font_var = tk.StringVar(value="Arial")
        self.font_size_var = tk.StringVar(value="12")
        
        # Initialize file variable
        self.current_file = None
        self.is_file_modified = False

        # Toolbar and text area setup
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.text_area = tk.Text(self.root, wrap='word', undo=True)
        self.text_area.pack(fill='both', expand=True)

        # Create toolbar icons and functionality
        self.add_toolbar_icons()

        # Bind events to track file modifications
        self.text_area.bind("<<Modified>>", self.on_text_modified)

    def add_toolbar_icons(self):
        """Adds icons to the toolbar for various functionalities."""
        icon_size = (24, 24)
        
        # Icons for toolbar buttons
        icons = {
            "file": Image.open("static/save-icon.png").resize(icon_size, Image.LANCZOS),
            "clipboard": Image.open("static/clipboard-icon.png").resize(icon_size, Image.LANCZOS),
            "bold": Image.open("static/bold-icon.png").resize(icon_size, Image.LANCZOS),
            "italic": Image.open("static/itallic-icon.png").resize(icon_size, Image.LANCZOS),
            "underline": Image.open("static/underline-icon.png").resize(icon_size, Image.LANCZOS),
            "text_color": Image.open("static/textcolor-icon.png").resize(icon_size, Image.LANCZOS),
            "insert_image": Image.open("static/image-icon.png").resize(icon_size, Image.LANCZOS),
            "insert_link": Image.open("static/link-icon.png").resize(icon_size, Image.LANCZOS),
            "change_font": Image.open("static/font-icon.png").resize(icon_size, Image.LANCZOS)
        }

        # Convert images to PhotoImage objects
        self.icons = {name: ImageTk.PhotoImage(icon) for name, icon in icons.items()}

        # File Button with Dropdown Menu
        file_button = tk.Menubutton(self.toolbar, image=self.icons["file"], relief=tk.RAISED)
        file_button.pack(side=tk.LEFT, padx=2, pady=2)
        file_button.menu = tk.Menu(file_button, tearoff=0)
        file_button["menu"] = file_button.menu
        self.create_file_menu(file_button.menu)

        # Clipboard Button with Dropdown Menu
        clipboard_button = tk.Menubutton(self.toolbar, image=self.icons["clipboard"], relief=tk.RAISED)
        clipboard_button.pack(side=tk.LEFT, padx=2, pady=2)
        clipboard_button.menu = tk.Menu(clipboard_button, tearoff=0)
        clipboard_button["menu"] = clipboard_button.menu
        self.create_clipboard_menu(clipboard_button.menu)

        # Font Button with Dropdown Menu
        font_button = tk.Menubutton(self.toolbar, image=self.icons["change_font"], relief=tk.RAISED)
        font_button.pack(side=tk.LEFT, padx=2, pady=2)
        font_button.menu = tk.Menu(font_button, tearoff=0)
        font_button["menu"] = font_button.menu
        self.create_font_menu(font_button.menu)

        # Other Toolbar Buttons
        tk.Button(self.toolbar, image=self.icons["bold"], command=self.make_bold).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(self.toolbar, image=self.icons["italic"], command=self.make_italic).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(self.toolbar, image=self.icons["underline"], command=self.make_underline).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(self.toolbar, image=self.icons["text_color"], command=self.change_text_color).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(self.toolbar, image=self.icons["insert_image"], command=self.insert_image).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(self.toolbar, image=self.icons["insert_link"], command=self.insert_link).pack(side=tk.LEFT, padx=2, pady=2)

    def create_file_menu(self, menu):
        """Creates a dropdown menu for file operations."""
        menu.add_command(label="New", command=self.new_file)
        menu.add_command(label="Open", command=self.open_file)
        menu.add_command(label="Save", command=self.save_file)
        menu.add_command(label="Save As", command=self.save_as_file)
        menu.add_command(label="Exit", command=self.exit_file)

    def create_clipboard_menu(self, menu):
        """Creates a dropdown menu for clipboard operations."""
        menu.add_command(label="Copy", command=self.copy_text)
        menu.add_command(label="Cut", command=self.cut_text)
        menu.add_command(label="Paste", command=self.paste_text)

    def create_font_menu(self, menu):
        """Creates a dropdown menu for selecting font family and size."""
        font_families = sorted(font.families())

        # Create submenu for font families
        font_family_menu = tk.Menu(menu, tearoff=False)
        for family in font_families:
            font_family_menu.add_radiobutton(label=family, variable=self.font_var, command=self.apply_font)
        
        # Create submenu for font sizes
        font_size_menu = tk.Menu(menu, tearoff=False)
        for size in range(8, 72, 2):
            font_size_menu.add_radiobutton(label=str(size), variable=self.font_size_var, command=self.apply_font)
        
        menu.add_cascade(label="Font Family", menu=font_family_menu)
        menu.add_cascade(label="Font Size", menu=font_size_menu)

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
        if self.is_file_modified:
            if not self.ask_save_changes():
                return
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.is_file_modified = False

    def open_file(self):
        if self.is_file_modified:
            if not self.ask_save_changes():
                return
        self.current_file = filedialog.askopenfilename(defaultextension=".txt",
                                                       filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.current_file:
            with open(self.current_file, "r") as file:
                content = file.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.is_file_modified = False

    def save_file(self):
        if not self.current_file:
            self.save_as_file()
        else:
            with open(self.current_file, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
                self.is_file_modified = False

    def save_as_file(self):
        self.current_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                         filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
                self.is_file_modified = False

    def exit_file(self):
        if self.is_file_modified:
            if not self.ask_save_changes():
                return
        
        # Close the current application
        self.root.destroy()
        
        # Start homepage.py
        script_path = os.path.abspath("homepage.py")
        subprocess.Popen([sys.executable, script_path])
        
        # Optionally, you could terminate the current script if needed
        # sys.exit()

    def ask_save_changes(self):
        """Prompt the user to save changes if the file is modified."""
        response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save them?")
        if response:  # Yes
            self.save_file()
            return True
        elif response is False:  # No
            return True
        else:  # Cancel
            return False

    def on_text_modified(self, event):
        """Update the modified status when text changes."""
        self.is_file_modified = True

    def make_bold(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "bold" in current_tags:
            self.text_area.tag_remove("bold", "sel.first", "sel.last")
        else:
            bold_font = font.Font(self.text_area, self.text_area.cget("font"))
            bold_font.configure(weight="bold")
            self.text_area.tag_configure("bold", font=bold_font)
            self.text_area.tag_add("bold", "sel.first", "sel.last")

    def make_italic(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "italic" in current_tags:
            self.text_area.tag_remove("italic", "sel.first", "sel.last")
        else:
            italic_font = font.Font(self.text_area, self.text_area.cget("font"))
            italic_font.configure(slant="italic")
            self.text_area.tag_configure("italic", font=italic_font)
            self.text_area.tag_add("italic", "sel.first", "sel.last")

    def make_underline(self):
        current_tags = self.text_area.tag_names("sel.first")
        if "underline" in current_tags:
            self.text_area.tag_remove("underline", "sel.first", "sel.last")
        else:
            underline_font = font.Font(self.text_area, self.text_area.cget("font"))
            underline_font.configure(underline=1)
            self.text_area.tag_configure("underline", font=underline_font)
            self.text_area.tag_add("underline", "sel.first", "sel.last")

    def insert_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            image = Image.open(file_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)
            self.text_area.image_create(tk.END, image=photo)
            self.text_area.image_list.append(photo)  # Save reference

    def insert_link(self):
        """Insert a hyperlink into the text area."""
        url = simpledialog.askstring("Insert Link", "Enter URL:")
        if url:
            self.text_area.insert(tk.INSERT, url)
            self.text_area.tag_add("hyperlink", tk.INSERT + "-%dc" % len(url), tk.INSERT)
            self.text_area.tag_config("hyperlink", foreground="blue", underline=True)
            self.text_area.tag_bind("hyperlink", "<Button-1>", lambda e: webbrowser.open(url))

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()