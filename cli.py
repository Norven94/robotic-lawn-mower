from dataclasses import dataclass

import inquirer
from enum import Enum

from settings import DEFAULT_ROBOT_NAME

#def alternativen i en Enum
class SimOption(Enum):
    RANDOM = ("random", "Slumpmässig rörelse")
    WIRED = ("wired", "Utsatt slinga")

    def __init__(self, key, label):
        self.key = key
        self.label = label

@dataclass
class CLI(): 
    # Skapa listan med labels för inquirer (de som kommer visas för användaren)
    choices = [option.label for option in SimOption]
        
    questions = [
        inquirer.List(
            "choice", #namnet på variablen där svaret sparas temporärt
            message = "Välj körläge", #text som visas för användare
            choices = choices, #de alternativ användaren kan välja mellan
        )        
    ]

    def startApplication (self, simulation_option: str | None) -> None:
        #fråga användaren efetr namn på roboten
        namn_input = input("Vad ska robotgräsklipparen heta? ")
        #om användaren inte skriver något, sätt namnet till "Per" annars, sätt namnet till det användaren skrev in.
        if namn_input == "":
            robot_namn = DEFAULT_ROBOT_NAME
        else:
            robot_namn = namn_input

        print("Robotgräsklipparen heter " + robot_namn + "!")

        while True:
            #hämta svaret (labeln) från användaren 
            selected_label = inquirer.prompt(self.questions)["choice"] #hämta det valda alternativet från svaret

            #Hitta vilket Enum-objek som matchar valda labeln
            answer = next(opt for opt in SimOption if opt.label == selected_label)
            simulation_option = answer.key

            if answer == SimOption.RANDOM:
                print("Du har valt: " + answer.label) #skriver ut det som står i parantesen
            elif answer == SimOption.WIRED:
                print("Du har valt: " + answer.label) #skriver ut det som står i parantesen

            break #bryter loopen och avslutar programmet efter valet

        #skriver ut en välkomsthälsning varje gång loopen börjar om
        print("Välkommen till robotgräsklipparen!")