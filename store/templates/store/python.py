dictionnaire={
    "professeur":"est une personne qui enseigne ou qui instruit",
    "informatique":"est le traitement automatique de l'information",
    "ordinateur":"est une machine electronique capable d'automatiser des informations",
    "apprendre":"acquerir des connaissances",
    "intelligence":"etre doue dans quelques chose"
}
mot=input("donnez un mot a chercher ")
if mot in dictionnaire:
    print(f"le sens du {mot}:{dictionnaire[mot]} ")
else:
    print(f"ce mot {mot} n'est pas dans mon dictionnaire")
new=input("voulez-vous connaitre le sens d'un autre mot?? (oui non)")
if new=="oui":
    mot=input("donnez le mot a chercher ")
    if mot in dictionnaire:
        print(f"le sens de {mot}:{dictionnaire[mot]}")
    else:
        print("ce mot n'est pas dedans") 
if new=="non":
    print("ok a la prochaine")    
