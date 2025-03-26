import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class ExplorateurFichiers:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Explorateur de Fichiers")
        self.fenetre.geometry("1000x600")

        # Configuration
        self.couleur_fond = "#f5f5f5"
        self.couleur_sidebar = "#2c3e50"
        self.couleur_selection = "#3498db"
        self.emoji_dossier = "📁 "
        self.emoji_fichier = "📄 "

        # Variables
        self.chemin_actuel = os.path.expanduser("~")
        self.favoris = set()
        self.historique = []
        self.position_historique = -1
        self.afficher_caches = False

        # Initialisation
        self.creer_interface()
        self.charger_favoris()
        self.naviguer(self.chemin_actuel)

    def creer_interface(self):
        # Barre d'outils
        toolbar = tk.Frame(self.fenetre, bg=self.couleur_sidebar, height=40)
        toolbar.pack(fill=tk.X)

        # Boutons navigation
        tk.Button(toolbar, text="←", command=self.retour, bg=self.couleur_sidebar, 
                 fg="white", borderwidth=0).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="→", command=self.suivant, bg=self.couleur_sidebar,
                 fg="white", borderwidth=0).pack(side=tk.LEFT)

        # Barre de chemin
        self.var_chemin = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.var_chemin, width=50).pack(side=tk.LEFT, padx=10)
        self.var_chemin.trace("w", lambda *args: self.changer_chemin_manuel())

        # Bouton fichiers cachés
        self.btn_caches = tk.Button(toolbar, text="👁 Cachés", command=self.basculer_caches,
                                  bg=self.couleur_sidebar, fg="white")
        self.btn_caches.pack(side=tk.LEFT, padx=5)

        # Bouton actualiser
        tk.Button(toolbar, text="🔄", command=self.actualiser, bg=self.couleur_sidebar,
                 fg="white", borderwidth=0).pack(side=tk.LEFT, padx=5)

        # Panneau principal
        main_panel = tk.PanedWindow(self.fenetre)
        main_panel.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(main_panel, width=200, bg=self.couleur_sidebar)
        main_panel.add(self.sidebar)
        
        tk.Label(self.sidebar, text="FAVORIS", bg=self.couleur_sidebar, 
                fg="white", font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.liste_favoris = tk.Listbox(self.sidebar, bg=self.couleur_sidebar, 
                                      fg="white", selectbackground=self.couleur_selection)
        self.liste_favoris.pack(fill=tk.BOTH, expand=True)
        self.liste_favoris.bind("<Double-Button-1>", self.ouvrir_favori)

        # Liste des fichiers
        file_frame = tk.Frame(main_panel)
        main_panel.add(file_frame, stretch="always")
        
        scroll = ttk.Scrollbar(file_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.liste_fichiers = tk.Listbox(file_frame, yscrollcommand=scroll.set,
                                       font=('Arial', 11), selectbackground="#e0e0e0")
        self.liste_fichiers.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.liste_fichiers.yview)

        # Événements
        self.liste_fichiers.bind("<Double-Button-1>", self.ouvrir_element)
        self.liste_fichiers.bind("<Button-3>", self.afficher_menu_contextuel)

        # Barre de statut
        self.barre_statut = tk.Label(self.fenetre, text="Prêt", anchor=tk.W,
                                    bg=self.couleur_sidebar, fg="white")
        self.barre_statut.pack(fill=tk.X)

    def basculer_caches(self):
        """Basculer l'affichage des fichiers cachés"""
        self.afficher_caches = not self.afficher_caches
        if self.afficher_caches:
            self.btn_caches.config(fg="#4CAF50")  # Vert quand activé
        else:
            self.btn_caches.config(fg="white")    # Blanc quand désactivé
        self.naviguer(self.chemin_actuel)

    def get_contenu(self):
        """Retourne la liste des éléments selon les paramètres"""
        contenu = []
        for f in os.listdir(self.chemin_actuel):
            if not self.afficher_caches and f.startswith('.'):
                continue
            contenu.append(f)
        return sorted(contenu)

    def naviguer(self, chemin):
        try:
            # Mise à jour historique
            if self.position_historique == -1 or self.historique[self.position_historique] != chemin:
                self.historique = self.historique[:self.position_historique+1]
                self.historique.append(chemin)
                self.position_historique = len(self.historique) - 1

            self.chemin_actuel = chemin
            self.var_chemin.set(chemin)
            self.liste_fichiers.delete(0, tk.END)

            # Dossier parent
            if chemin != os.path.expanduser("~"):
                self.liste_fichiers.insert(tk.END, self.emoji_dossier + "..")

            # Contenu du dossier
            for f in self.get_contenu():
                full_path = os.path.join(chemin, f)
                prefix = self.emoji_dossier if os.path.isdir(full_path) else self.emoji_fichier
                self.liste_fichiers.insert(tk.END, prefix + f)

            self.barre_statut.config(text=f"{len(self.get_contenu())} éléments | {chemin}")

        except PermissionError:
            messagebox.showerror("Erreur", "Accès refusé !")
            self.retour()
        except FileNotFoundError:
            messagebox.showerror("Erreur", "Dossier introuvable !")
            self.retour()

    def retour(self):
        if self.position_historique > 0:
            self.position_historique -= 1
            self.naviguer(self.historique[self.position_historique])

    def suivant(self):
        if self.position_historique < len(self.historique) - 1:
            self.position_historique += 1
            self.naviguer(self.historique[self.position_historique])

    def changer_chemin_manuel(self):
        nouveau_chemin = self.var_chemin.get()
        if os.path.exists(nouveau_chemin):
            self.naviguer(nouveau_chemin)
        else:
            messagebox.showerror("Erreur", "Chemin invalide")
            self.var_chemin.set(self.chemin_actuel)

    def ouvrir_element(self, event):
        selection = self.liste_fichiers.curselection()
        if selection:
            element = self.liste_fichiers.get(selection[0])
            element = element.replace(self.emoji_dossier, "").replace(self.emoji_fichier, "")
            
            if element == "..":
                self.naviguer(os.path.dirname(self.chemin_actuel))
            else:
                full_path = os.path.join(self.chemin_actuel, element)
                if os.path.isdir(full_path):
                    self.naviguer(full_path)
                else:
                    try:
                        os.startfile(full_path)
                    except:
                        messagebox.showinfo("Information", f"Impossible d'ouvrir : {element}")

    def afficher_menu_contextuel(self, event):
        selection = self.liste_fichiers.curselection()
        if selection:
            element = self.liste_fichiers.get(selection[0])
            element = element.replace(self.emoji_dossier, "").replace(self.emoji_fichier, "")
            full_path = os.path.join(self.chemin_actuel, element)

            menu = tk.Menu(self.fenetre, tearoff=0)
            menu.add_command(label="Ouvrir", command=lambda: self.ouvrir_element(event))
            menu.add_separator()
            
            if full_path in self.favoris:
                menu.add_command(label="Retirer des favoris", command=lambda: self.retirer_favori(full_path))
            else:
                menu.add_command(label="Ajouter aux favoris", command=lambda: self.ajouter_favori(full_path))
            
            menu.add_command(label="Renommer", command=lambda: self.renommer(full_path))
            menu.add_command(label="Supprimer", command=lambda: self.supprimer(full_path))
            menu.add_command(label="Propriétés", command=lambda: self.afficher_proprietes(full_path))
            
            menu.tk_popup(event.x_root, event.y_root)

    def charger_favoris(self):
        try:
            with open("favoris.txt", "r") as f:
                self.favoris = set(line.strip() for line in f.readlines())
        except FileNotFoundError:
            self.favoris = set()

    def sauvegarder_favoris(self):
        with open("favoris.txt", "w") as f:
            for fav in self.favoris:
                f.write(fav + "\n")

    def ajouter_favori(self, chemin):
        self.favoris.add(chemin)
        self.sauvegarder_favoris()
        self.mettre_a_jour_favoris()

    def retirer_favori(self, chemin):
        if chemin in self.favoris:
            self.favoris.remove(chemin)
            self.sauvegarder_favoris()
            self.mettre_a_jour_favoris()

    def mettre_a_jour_favoris(self):
        self.liste_favoris.delete(0, tk.END)
        for fav in sorted(self.favoris):
            self.liste_favoris.insert(tk.END, fav)

    def ouvrir_favori(self, event):
        selection = self.liste_favoris.curselection()
        if selection:
            chemin = self.liste_favoris.get(selection[0])
            if os.path.exists(chemin):
                if os.path.isdir(chemin):
                    self.naviguer(chemin)
                else:
                    os.startfile(chemin)

    def actualiser(self):
        self.naviguer(self.chemin_actuel)

    def creer_dossier(self):
        nom = simpledialog.askstring("Nouveau dossier", "Nom du dossier:")
        if nom:
            try:
                os.mkdir(os.path.join(self.chemin_actuel, nom))
                self.naviguer(self.chemin_actuel)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def renommer(self, chemin):
        nouveau_nom = simpledialog.askstring("Renommer", "Nouveau nom:", 
                                            initialvalue=os.path.basename(chemin))
        if nouveau_nom:
            try:
                nouveau_chemin = os.path.join(os.path.dirname(chemin), nouveau_nom)
                os.rename(chemin, nouveau_chemin)
                self.naviguer(self.chemin_actuel)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def supprimer(self, chemin):
        if messagebox.askyesno("Confirmer", f"Supprimer {os.path.basename(chemin)} ?"):
            try:
                if os.path.isdir(chemin):
                    os.rmdir(chemin)
                else:
                    os.remove(chemin)
                self.naviguer(self.chemin_actuel)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def afficher_proprietes(self, chemin):
        stats = os.stat(chemin)
        message = f"Nom: {os.path.basename(chemin)}\n"
        message += f"Type: {'Dossier' if os.path.isdir(chemin) else 'Fichier'}\n"
        message += f"Taille: {stats.st_size:,} octets\n"
        message += f"Créé le: {datetime.fromtimestamp(stats.st_ctime)}\n"
        message += f"Modifié le: {datetime.fromtimestamp(stats.st_mtime)}"
        messagebox.showinfo("Propriétés", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExplorateurFichiers(root)
    root.mainloop()
