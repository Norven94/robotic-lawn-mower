import inquirer

while True:
    print("Välkommen till robotgräsklipparen!")

    # Skapa listan med val
    questions = [
        inquirer.List(
            "choice",
            message="Välj körläge",
            choices=["Slumpmässig rörelse", "Utsatt slinga"],
        )        
    ]

    # Hämta svaret från användaren (Se till att denna ligger rakt under 'questions')
    answer = inquirer.prompt(questions)["choice"]

    if answer == "Slumpmässig rörelse":
        print("Du har valt slumpmässig rörelse.")
        break
    elif answer == "Utsatt slinga":
        print("Du har valt utsatt slinga.")
        break