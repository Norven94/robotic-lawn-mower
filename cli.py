from dataclasses import dataclass

import inquirer
from enum import Enum

import appState
from settings import DEFAULT_ROBOT_NAME

#def alternativen i en Enum
class SimOption(Enum):
    GPS_NO = ("gps_no", "GPS med specifikt rörelsemönster (utan hinder)")
    GPS_YES = ("gps_yes", "GPS med specifikt rörelsemönster (med hinder)")
    WIRED_NO = ("wired_no", "Utsatt slinga med slumpmässig rörelse (utan hinder)")
    WIRED_YES = ("wired_yes", "Utsatt slinga med slumpmässig rörelse (med hinder)")

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

    def startApplication(self, appState) -> str:
        #fråga användaren efetr namn på roboten
        namn_input = input("Vad ska robotgräsklipparen heta? ")
        #om användaren inte skriver något, sätt namnet till "Per" annars, sätt namnet till det användaren skrev in.
        if namn_input == "":
            robot_namn = DEFAULT_ROBOT_NAME
        else:
            robot_namn = namn_input

        appState.robot_name = robot_namn #spara robotnamnet i appState så att det kan användas i hela programmet

        print("Robotgräsklipparen heter " + robot_namn + "!")

        while True:
            #hämta svaret (labeln) från användaren 
            answers = inquirer.prompt(self.questions)
            if not answers:
                continue
            selected_label = answers["choice"] #hämta det valda alternativet från svaret

            #Hitta vilket Enum-objek som matchar valda labeln
            selected_option = next(opt for opt in SimOption if opt.label == selected_label)
            
            if "gps" in selected_option.key:
                print("Du har valt: " + selected_option.label) #skriver ut det som står i parantesen
            else: 
                print("Du har valt: " + selected_option.label) #skriver ut det som står i parantesen

            break #bryter loopen och avslutar programmet efter valet

        #skriver ut en välkomsthälsning varje gång loopen börjar om
        print("Välkommen till robotgräsklipparen!")
        return selected_option.key #returnerar nyckeln för det valda alternativet (t.ex. "gps_no")