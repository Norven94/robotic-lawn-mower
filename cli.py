from dataclasses import dataclass

import inquirer
from enum import Enum

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

class SimulationModeOption(Enum):
    ANIMATED = (True, "Animerad simulering")
    INSTANT = (False, "Direkt simulering")

    def __init__(self, animate, label):
        self.animate = animate
        self.label = label

@dataclass
class CLI(): 
    # Skapa listan med labels för inquirer (de som kommer visas för användaren)
    sim_choices = [option.label for option in SimOption]
    obstacle_choices = [option.label for option in ObstacleOption]
    simulation_mode_choices = [option.label for option in SimulationModeOption]
        
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
        ),
        inquirer.List(
            "simulation_mode_choice",
            message = "Välj hur simuleringen ska köras",
            choices = simulation_mode_choices,
        )
    ]

    def startApplication(self, appState):
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

        selected_mode_label = answers["simulation_mode_choice"]
        simulation_mode_enum = next(opt for opt in SimulationModeOption if opt.label == selected_mode_label)
        animate_simulation = simulation_mode_enum.animate

        #Spara i appstate
        appState.simulation_option = simulation_option
        appState.has_obstacles = has_obstacles
        appState.animate_simulation = animate_simulation

        simulation_mode_text = "animerad" if animate_simulation else "direkt"
        print(f"Du har valt {simulation_option} {'med' if has_obstacles else 'utan'} hinder i {simulation_mode_text} läge.")