n = 3
print("Je vais vous demander", n, "nombres")
for i in range(n):
    x = int(input("Donnez un nombre : "))
    if x > 0:
        print(x, "est positif")
    else:
        print(x, "est négatif ou nul")
print("Fin")