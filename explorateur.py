import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("File Explorer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # Configuration
        self.current_path = os.path.expanduser("~")
        self.history = []
        self.history_position = -1
        self.favorites = set()
        self.search_query = tk.StringVar()
        self.view_mode = "grid"  # 'grid' ou 'list'

        # UI Setup
        self.setup_sidebar()
        self.setup_main_content()
        self.setup_statusbar()
        
        # Initial load
        self.load_favorites()
        self.navigate_to(self.current_path)

    def setup_sidebar(self):
        sidebar = tk.Frame(self.root, width=250, bg="#e0e0e0", relief="sunken", borderwidth=2)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(5,2), pady=5)
        
        # Recents section
        tk.Label(sidebar, text="# Recents", bg="#e0e0e0", anchor="w", 
                font=('Arial', 9, 'bold')).pack(fill=tk.X, padx=5, pady=(10,0))
        self.recents_list = tk.Listbox(sidebar, bg="#e0e0e0", borderwidth=0, 
                                      highlightthickness=0, height=4, font=('Arial', 9))
        self.recents_list.pack(fill=tk.X, padx=5, pady=(0,5))
        
        # Favorites section
        tk.Label(sidebar, text="## Favorites", bg="#e0e0e0", anchor="w",
                font=('Arial', 9, 'bold')).pack(fill=tk.X, padx=5, pady=(10,0))
        self.favorites_list = tk.Listbox(sidebar, bg="#e0e0e0", borderwidth=0,
                                        highlightthickness=0, height=8, font=('Arial', 9))
        self.favorites_list.pack(fill=tk.X, padx=5, pady=(0,5))
        self.favorites_list.bind("<Double-Button-1>", self.open_favorite)
        
        # Computer Tags section
        tk.Label(sidebar, text="### Computer Tags", bg="#e0e0e0", anchor="w",
                font=('Arial', 9, 'bold')).pack(fill=tk.X, padx=5, pady=(10,0))
        self.tags_list = tk.Listbox(sidebar, bg="#e0e0e0", borderwidth=0,
                                  highlightthickness=0, height=4, font=('Arial', 9))
        self.tags_list.pack(fill=tk.X, padx=5, pady=(0,5))

    def setup_main_content(self):
        main_frame = tk.Frame(self.root, bg="#ffffff", relief="raised", borderwidth=1)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2,5), pady=5)
        
        # Path display
        path_frame = tk.Frame(main_frame, bg="#ffffff")
        path_frame.pack(fill=tk.X, padx=10, pady=10)
        self.path_label = tk.Label(path_frame, text="/root/current/path", bg="#ffffff",
                                  anchor="w", font=('Arial', 10, 'bold'))
        self.path_label.pack(fill=tk.X)
        
        # Toolbar
        toolbar = tk.Frame(main_frame, bg="#ffffff")
        toolbar.pack(fill=tk.X, pady=(0,10))
        
        # Navigation buttons
        btn_style = {'bg':'#ffffff', 'borderwidth':0, 'activebackground':'#f0f0f0'}
        tk.Button(toolbar, text="←", command=self.navigate_back, **btn_style).pack(side=tk.LEFT)
        tk.Button(toolbar, text="→", command=self.navigate_forward, **btn_style).pack(side=tk.LEFT)
        tk.Button(toolbar, text="🔄", command=self.refresh_view, **btn_style).pack(side=tk.LEFT)
        
        # View toggle button
        self.view_btn = tk.Button(toolbar, text="☰", command=self.toggle_view_mode,
                                bg="#e0e0e0", relief="flat")
        self.view_btn.pack(side=tk.RIGHT, padx=5)
        
        # Create folder button
        tk.Button(toolbar, text="+ Dossier", command=self.create_folder, 
                 bg="#e0e0e0", relief="flat").pack(side=tk.RIGHT, padx=5)
        
        # Search bar
        search_frame = tk.Frame(main_frame, bg="#ffffff")
        search_frame.pack(fill=tk.X, pady=(0,10), padx=10)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_items())
        tk.Entry(search_frame, textvariable=self.search_var, relief="sunken",
                borderwidth=1).pack(fill=tk.X, ipady=2)
        
        # Files display container
        self.files_container = tk.Frame(main_frame, bg="#ffffff")
        self.files_container.pack(fill=tk.BOTH, expand=True)
        
        # Setup both views
        self.setup_grid_view()
        self.setup_list_view()
        self.show_current_view()

    def setup_grid_view(self):
        """Configure la vue en grille avec cases à cocher"""
        self.grid_frame = tk.Frame(self.files_container, bg="#ffffff")
        
        self.grid_canvas = tk.Canvas(self.grid_frame, bg="#ffffff", highlightthickness=0)
        self.grid_scroll = ttk.Scrollbar(self.grid_frame, orient="vertical", 
                                       command=self.grid_canvas.yview)
        self.grid_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.grid_canvas.configure(yscrollcommand=self.grid_scroll.set)
        
        self.folders_frame = tk.Frame(self.grid_canvas, bg="#ffffff")
        self.grid_canvas.create_window((0, 0), window=self.folders_frame, anchor="nw")
        
        for i in range(3):
            self.folders_frame.grid_columnconfigure(i, weight=1, uniform="cols")
        
        self.folders_frame.bind("<Configure>", 
                              lambda e: self.grid_canvas.configure(
                                  scrollregion=self.grid_canvas.bbox("all")))

    def setup_list_view(self):
        """Configure la vue en liste traditionnelle"""
        self.list_frame = tk.Frame(self.files_container, bg="#ffffff")
        
        self.list_scroll = ttk.Scrollbar(self.list_frame)
        self.list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(self.list_frame, yscrollcommand=self.list_scroll.set,
                                bg="#ffffff", font=('Arial', 11), selectbackground="#e0e0e0")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.list_scroll.config(command=self.listbox.yview)
        
        self.listbox.bind("<Double-Button-1>", self.open_item_list)
        self.listbox.bind("<Button-3>", self.show_context_menu_list)

    def setup_statusbar(self):
        self.status = tk.Label(self.root, text="Ready", anchor=tk.W, bg="#e0e0e0",
                             font=('Arial', 9), padx=10)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def load_favorites(self):
        """Charge les favoris depuis le fichier"""
        try:
            with open("favorites.txt", "r") as f:
                self.favorites = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            self.favorites = set()
        self.update_favorites_list()

    def update_favorites_list(self):
        """Met à jour la liste des favoris dans la sidebar"""
        self.favorites_list.delete(0, tk.END)
        for fav in sorted(self.favorites):
            self.favorites_list.insert(tk.END, os.path.basename(fav))

    def open_favorite(self, event):
        """Ouvre un favori sélectionné"""
        selection = self.favorites_list.curselection()
        if selection:
            fav_name = self.favorites_list.get(selection[0])
            for path in self.favorites:
                if os.path.basename(path) == fav_name:
                    self.navigate_to(path)
                    break

    def navigate_to(self, path):
        """Navigue vers le chemin spécifié"""
        try:
            if not os.path.exists(path):
                raise FileNotFoundError
            
            # Update history
            if not self.history or self.history[self.history_position] != path:
                self.history = self.history[:self.history_position+1]
                self.history.append(path)
                self.history_position = len(self.history) - 1
            
            self.current_path = path
            self.update_path_display()
            self.display_items()
            
            # Update recents
            self.recents_list.delete(0, tk.END)
            for i, recent in enumerate(reversed(self.history[-5:])):
                self.recents_list.insert(0, os.path.basename(recent))
            
            self.status.config(text=f"Viewing: {path}")

        except PermissionError:
            messagebox.showerror("Error", "Access denied!")
        except FileNotFoundError:
            messagebox.showerror("Error", "Path not found!")

    def update_path_display(self):
        """Met à jour l'affichage du chemin actuel"""
        self.path_label.config(text=self.current_path)

    def display_items(self):
        """Affiche les éléments selon le mode de vue actuel"""
        if self.view_mode == "grid":
            self.display_folders_grid()
        else:
            self.display_folders_list()

    def display_folders_grid(self):
        """Affiche les dossiers en mode grille"""
        for widget in self.folders_frame.winfo_children():
            widget.destroy()
        
        items = self.get_filtered_items()
        if items is None:
            return
        
        for i, (name, path) in enumerate(sorted(items)):
            row, col = divmod(i, 3)
            
            frame = tk.Frame(self.folders_frame, bg="#ffffff")
            frame.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
            
            # Checkbox
            tk.Checkbutton(frame, bg="#ffffff", activebackground="#ffffff").pack()
            
            # Folder name
            lbl = tk.Label(frame, text=name, bg="#ffffff", font=('Arial', 10, 'bold'))
            lbl.pack()
            
            # Bindings
            lbl.bind("<Double-Button-1>", lambda e, p=path: self.navigate_to(p))
            lbl.bind("<Button-3>", lambda e, p=path: self.show_context_menu(e, p))

        self.folders_frame.update_idletasks()
        self.grid_canvas.config(scrollregion=self.grid_canvas.bbox("all"))

    def display_folders_list(self):
        """Affiche les dossiers en mode liste"""
        self.listbox.delete(0, tk.END)
        
        items = self.get_filtered_items()
        if items is None:
            return
        
        for name, path in sorted(items):
            self.listbox.insert(tk.END, name)
            # Store paths for listbox items
            if not hasattr(self.listbox, 'paths'):
                self.listbox.paths = {}
            self.listbox.paths[self.listbox.size()-1] = path

    def get_filtered_items(self):
        """Retourne les éléments filtrés selon la recherche"""
        items = []
        try:
            for item in os.listdir(self.current_path):
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    items.append((item, full_path))
        except PermissionError:
            messagebox.showerror("Error", "Cannot read directory contents!")
            return None
        
        # Filter by search term
        search_term = self.search_var.get().lower()
        return [i for i in items if not search_term or search_term in i[0].lower()]

    def open_item_list(self, event):
        """Gère l'ouverture d'un élément en mode liste"""
        selection = self.listbox.curselection()
        if selection:
            path = self.listbox.paths[selection[0]]
            self.navigate_to(path)

    def show_context_menu_list(self, event):
        """Affiche le menu contextuel en mode liste"""
        selection = self.listbox.curselection()
        if selection:
            path = self.listbox.paths[selection[0]]
            self.show_context_menu(event, path)

    def show_context_menu(self, event, path):
        """Affiche le menu contextuel pour un élément"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Open", command=lambda: self.navigate_to(path))
        menu.add_separator()
        
        if path in self.favorites:
            menu.add_command(label="Remove from Favorites", 
                           command=lambda: self.remove_favorite(path))
        else:
            menu.add_command(label="Add to Favorites", 
                           command=lambda: self.add_favorite(path))
        
        menu.add_command(label="Rename", command=lambda: self.rename_item(path))
        menu.add_command(label="Delete", command=lambda: self.delete_item(path))
        menu.add_command(label="Properties", command=lambda: self.show_properties(path))
        
        menu.tk_popup(event.x_root, event.y_root)

    def add_favorite(self, path):
        """Ajoute un chemin aux favoris"""
        self.favorites.add(path)
        with open("favorites.txt", "w") as f:
            for fav in sorted(self.favorites):
                f.write(f"{fav}\n")
        self.update_favorites_list()

    def remove_favorite(self, path):
        """Retire un chemin des favoris"""
        if path in self.favorites:
            self.favorites.remove(path)
            with open("favorites.txt", "w") as f:
                for fav in sorted(self.favorites):
                    f.write(f"{fav}\n")
            self.update_favorites_list()

    def navigate_back(self):
        """Retourne à l'élément précédent dans l'historique"""
        if self.history_position > 0:
            self.history_position -= 1
            self.navigate_to(self.history[self.history_position])

    def navigate_forward(self):
        """Avance à l'élément suivant dans l'historique"""
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            self.navigate_to(self.history[self.history_position])

    def refresh_view(self):
        """Rafraîchit l'affichage"""
        self.display_items()

    def toggle_view_mode(self):
        """Bascule entre les modes d'affichage"""
        self.view_mode = "list" if self.view_mode == "grid" else "grid"
        self.show_current_view()

    def show_current_view(self):
        """Affiche le mode de vue actuel"""
        if self.view_mode == "grid":
            self.list_frame.pack_forget()
            self.grid_frame.pack(fill=tk.BOTH, expand=True)
            self.view_btn.config(text="☰")
            self.display_folders_grid()
        else:
            self.grid_frame.pack_forget()
            self.list_frame.pack(fill=tk.BOTH, expand=True)
            self.view_btn.config(text="🟀")
            self.display_folders_list()

    def create_folder(self):
        """Crée un nouveau dossier"""
        name = simpledialog.askstring("New Folder", "Folder name:")
        if name:
            try:
                os.mkdir(os.path.join(self.current_path, name))
                self.display_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def rename_item(self, path):
        """Renomme un dossier ou fichier"""
        new_name = simpledialog.askstring("Rename", "New name:", 
                                        initialvalue=os.path.basename(path))
        if new_name:
            try:
                new_path = os.path.join(os.path.dirname(path), new_name)
                os.rename(path, new_path)
                
                if path in self.favorites:
                    self.remove_favorite(path)
                    self.add_favorite(new_path)
                    
                self.display_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_item(self, path):
        """Supprime un dossier ou fichier"""
        if not messagebox.askyesno("Confirm", f"Delete {os.path.basename(path)}?"):
            return
            
        try:
            os.rmdir(path) if os.path.isdir(path) else os.remove(path)
            
            if path in self.favorites:
                self.remove_favorite(path)
                
            self.display_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_properties(self, path):
        """Affiche les propriétés d'un élément"""
        try:
            stats = os.stat(path)
            info = (
                f"Name: {os.path.basename(path)}\n"
                f"Type: {'Folder' if os.path.isdir(path) else 'File'}\n"
                f"Size: {stats.st_size:,} bytes\n"
                f"Created: {datetime.fromtimestamp(stats.st_ctime)}\n"
                f"Modified: {datetime.fromtimestamp(stats.st_mtime)}"
            )
            messagebox.showinfo("Properties", info)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def filter_items(self):
        """Filtre les éléments selon la recherche"""
        self.display_items()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()
