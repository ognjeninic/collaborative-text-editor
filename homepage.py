import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import os

class HomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Page")

        # Lista fajlova
        self.file_listbox = tk.Listbox(self.root, height=15, width=50)
        self.file_listbox.pack(pady=20)

        # Dugmad
        self.open_button = tk.Button(self.root, text="Open File", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=10, pady=(0,15))

        self.new_button = tk.Button(self.root, text="New File", command=self.new_file)
        self.new_button.pack(side=tk.LEFT, padx=10, pady=(0,15))

        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.upload_button.pack(side=tk.LEFT, padx=10, pady=(0,15))

        self.delete_button = tk.Button(self.root, text="Delete File", command=self.delete_file)
        self.delete_button.pack(side=tk.LEFT, padx=10, pady=(0,15))


        self.load_files()

        # Bind Esc key to toggle fullscreen
        self.root.bind("<Escape>", self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        # Toggle fullscreen
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
        if not self.root.attributes("-fullscreen"):
            self.root.attributes("-topmost", True)
            self.root.attributes("-topmost", False)

    def load_files(self):
        """Učitaj fajlove iz documents.json i prikaži ih u listbox-u"""
        try:
            if not os.path.exists('documents.json'):
                with open('documents.json', 'w') as f:
                    json.dump({}, f, indent=4)
                    
            with open('documents.json', 'r') as f:
                data = json.load(f)
                # Proveri da li ima bilo kakve fajlove
                if not data:
                    self.file_listbox.delete(0, tk.END)  # Očisti prethodne stavke
                    return

                self.file_listbox.delete(0, tk.END)  # Očisti prethodne stavke
                for key, value in data.items():
                    self.file_listbox.insert(tk.END, value)
        except FileNotFoundError:
            messagebox.showerror("Error", "documents.json not found")

    def open_file(self):
        """Otvori odabrani fajl za izmenu"""
        selected_file = self.file_listbox.get(tk.ACTIVE)
        if selected_file:
            self.root.destroy()  # Zatvori home page
            os.system(f"python client.py {selected_file}")  # Pokreni editor sa odabranim fajlom

    def new_file(self):
        """Kreiraj novi fajl"""
        new_file_name = simpledialog.askstring("New File", "Enter file name:")
        if new_file_name:
            # Dodaj novi fajl u radni direktorijum
            with open(new_file_name, 'w') as f:
                f.write("")  # Kreiraj prazan fajl

            # Dodaj novi fajl u JSON listu
            with open('documents.json', 'r+') as f:
                data = json.load(f)
                print(data)
                # Kreiraj novi ključ i dodaj fajl
                new_key = str(len(data) + 1)
                data[new_key] = new_file_name
                f.seek(0)
                json.dump(data, f, indent=4)
            
            self.load_files()  # Osveži listu fajlova

    def upload_file(self):
        """Učitaj fajl sa računara i dodaj ga u listu"""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            file_name = os.path.basename(file_path)
            os.rename(file_path, file_name)  # Premesti fajl u radni direktorijum

            # Dodaj fajl u JSON listu
            with open('documents.json', 'r+') as f:
                data = json.load(f)
                # Kreiraj novi ključ i dodaj fajl
                new_key = str(len(data) + 1)
                data[new_key] = file_name
                f.seek(0)
                json.dump(data, f, indent=4)
            
            self.load_files()  # Osveži listu fajlova

    def delete_file(self):
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)  # Uzmimo ime fajla iz listbox-a
            result = messagebox.askyesno("Delete File", f"Are you sure you want to delete '{selected_file}'?")
            if result:
                # Ukloni fajl iz radnog direktorijuma
                if os.path.exists(selected_file):
                    os.remove(selected_file)
                
                # Ukloni fajl iz JSON liste
                with open('documents.json', 'r+') as f:
                    data = json.load(f)
                    
                    key_to_remove = None
                    for key, value in data.items():
                        if value == selected_file:
                            key_to_remove = key
                            break

                    if key_to_remove:
                        del data[key_to_remove]
                        f.seek(0)
                        f.truncate()  
                        json.dump(data, f, indent=4)
                
                self.load_files()  
        else:
            messagebox.showwarning("No Selection", "Please select a file to delete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HomePage(root)
    root.mainloop()
