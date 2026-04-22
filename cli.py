from dataclasses import dataclass

import inquirer
from enum import Enum

import appState
from settings import DEFAULT_ROBOT_NAME

#def alternativen i en Enum
class SimOption(Enum):
    GPS = ("gps", "GPS med specifikt rörelsemönster")
    WIRED = ("wired", "Utsatt slinga med slumpmässig rörelse")

    def __init__(self, key, label):
        self.key = key
        self.label = label

class ObstacleOption(Enum):
    WITH_OBSTACLES = ("with_obstacles", "Med hinder")
    WITHOUT_OBSTACLES = ("without_obstacles", "Utan hinder")

    def __init__(self, active, label):
        self.active = active
        self.label = label

@dataclass
class CLI(): 
    # Skapa listan med labels för inquirer (de som kommer visas för användaren)
    sim_choices = [option.label for option in SimOption]
    obstacle_choices = [option.label for option in ObstacleOption]
        
    questions = [
        inquirer.List(
            "sim_choice", #namnet på variablen där svaret sparas temporärt
            message = "Välj körläge", #text som visas för användare
            choices = sim_choices, #de alternativ användaren kan välja mellan
        ),
        inquirer.List(
            "obstacle_choice", #namnet på variablen där svaret sparas temporärt
            message = "Välj hinderalternativ", #text som visas för användare
            choices = obstacle_choices, #de alternativ användaren kan välja mellan
        )
    ]

    def startApplication(self, appState) -> tuple:
        #fråga användaren efetr namn på roboten
        namn_input = input("Vad ska robotgräsklipparen heta? ")
        #om användaren inte skriver något, sätt namnet till "Per" annars, sätt namnet till det användaren skrev in.
        if namn_input == "":
            robot_namn = DEFAULT_ROBOT_NAME
        else:
            robot_namn = namn_input
        appState.robot_name = robot_namn #spara namnet i appState så att det kan användas i resten av programmet
        print("Robotgräsklipparen heter " + robot_namn + "!")

        answers = inquirer.prompt(self.questions) #hämta svaren från användaren genom att visa frågorna

#Hantera SimOptiom
        selected_sim_label = answers["sim_choice"] #hämta det valda alternativet för simuleringsläge från svaret
        sim_enum = next(opt for opt in SimOption if opt.label == selected_sim_label) #hitta vilket Enum-objek som matchar valda labeln
        simulation_option = sim_enum.key #hämta nyckeln (t.ex. "gps") från det valda alternativet
#Hantera ObstacleOption
        selected_obstacle_label = answers["obstacle_choice"]
        obstacle_enum = next(opt for opt in ObstacleOption if opt.label == selected_obstacle_label) 
        has_obstacles = obstacle_enum.active == "with_obstacles"

#Spara i appstate
        appState.simulation_option = simulation_option
        appState.has_obstacles = has_obstacles

        print(f"Du har valt {simulation_option} {'med' if has_obstacles else 'utan'} hinder.")

        #skriver ut en välkomsthälsning varje gång loopen börjar om
        print("Välkommen till robotgräsklipparen!")
        
        return simulation_option #returnerar nyckeln för det valda alternativet (t.ex. "gps_no")
        return has_obstacles #returnerar om användaren vill ha hinder eller inte