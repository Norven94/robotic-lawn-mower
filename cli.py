import inquirer

while True:
    #skriver ut en välkomsthälsning varje gång loopen börjar om
    print("Välkommen till robotgräsklipparen!")

    # Skapa listan med val
    questions = [
        inquirer.List(
            "choice", #namnet på variablen där svaret sparas temporärt
            message="Välj körläge", #text som visas för användare
            choices=["Slumpmässig rörelse", "Utsatt slinga"], #de alternativ användaren kan välja mellan
        )        
    ]

    #hämta svaret från användaren (pilar + enter)
    #hämtar svaret via nyckeln - "choice"
    answer = inquirer.prompt(questions)["choice"]

    #logik för att hantera valen
    if answer == "Slumpmässig rörelse":
        print("Du har valt slumpmässig rörelse.") #skriver ut dte som står i parantesen
        break #bryter loopen och avslutar programmet efter valet
    elif answer == "Utsatt slinga":
        print("Du har valt utsatt slinga.")
        break
