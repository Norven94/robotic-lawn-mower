#Fråga användaren efter ett val av körläge
while True:
    print("Välkommen till robotgräskliparen!")
    print("Välj körläge:")
    print("1. Slumpmässig rörelse")
    print("2. Utsatt slinga")

    val = input("Välj körläge (1 eller 2): ") #input= stannar programmet och väntar på att användaren ska skriva in något
    #användaren väljer om de vill ha 1 eller 2
    if val == "1":
        print("Du har valt slumpmässig rörelse.")
        #lägga till kod för själva körningen här?
        break #hoppar ur loopen
    elif val == "2": #elif = else if, används för att kolla flera olika villkor
        print("Du har valt utsatt slinga.")
        #lägga till kod för själva körningen här?
        break #hoppar ur loopen
    else: #om användaren inte väljer 1 eller 2, skriv ut ett felmeddelande och fortsätt loopen eftersom den inte bryts (break)
        print("Ogiltigt val, vänligen försök igen!")