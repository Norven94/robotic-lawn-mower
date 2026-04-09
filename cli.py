import inquirer
from enum import Enum

#fråga användaren efetr namn på roboten
namn_input = input("Vad ska robotgräsklipparen heta? ")
#om användaren inte skriver något, sätt namnet till "Per" annars, sätt namnet till det användaren skrev in.
if namn_input == "":
    robot_namn = "Per"
else:
    robot_namn = namn_input

print("Robotgräsklipparen heter " + robot_namn + "!")

#def alternativen i en Enum
class SimOption(Enum):
    RANDOM = ("random", "Slumpmässig rörelse")
    WIRED = ("wired", "Utsatt slinga")

    def __init__(self, key, label):
        self.key = key
        self.label = label

# Skapa listan med labels för inquirer (de som kommer visas för användaren)
choices = [option.label for option in SimOption]
    
questions = [
    inquirer.List(
        "choice", #namnet på variablen där svaret sparas temporärt
        message = "Välj körläge", #text som visas för användare
        choices = choices, #de alternativ användaren kan välja mellan
    )        
]

while True:
    #skriver ut en välkomsthälsning varje gång loopen börjar om
    print("Välkommen till robotgräsklipparen!")

    #hämta svaret (labeln) från användaren 
    selected_label = inquirer.prompt(questions)["choice"] #hämta det valda alternativet från svaret

    #Hitta vilket Enum-objek som matchar valda labeln
    answer = next(opt for opt in SimOption if opt.label == selected_label)

    if answer == SimOption.RANDOM:
        print("Du har valt: " + answer.label) #skriver ut det som står i parantesen
    elif answer == SimOption.WIRED:
        print("Du har valt: " + answer.label) #skriver ut det som står i parantesen

    break #bryter loopen och avslutar programmet efter valet

