# Problèmes et Solutions

## 1. Actualisation de l'interface
*Problème* : L'interface ne se mettait pas à jour après certaines actions  
*Solution* : Implémenter la méthode `actualiser()` qui recharge le contenu du dossier

## 2. Gestion des fichiers cachés
*Problème* : Les fichiers cachés (.fichier) n'étaient pas filtrés  
*Solution* : Ajouter une variable booléenne `afficher_caches` et un filtre dans `get_contenu()`

## 3. Compatibilité multi-OS
*Problème* : Le comportement différait entre Windows et Linux  
*Solution* : Utiliser `os.path` pour les chemins et `os.startfile()` pour l'ouverture
