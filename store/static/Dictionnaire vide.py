Dictionnaire = {}
mot = input("Entrez le mot à ajouter :")
définition = input("Entrez la définition du mot :")
Dictionnaire[mot] = définition
mot_à_vérifier = input("Entrez le mot à vérifier :")
if mot_à_vérifier in Dictionnaire:
    print(f"définition de '{mot_à_vérifier}': {Dictionnaire [mot_à_vérifier]}")
else:
    print("le mot saisie est introuvable dans le Dictionnaire.")