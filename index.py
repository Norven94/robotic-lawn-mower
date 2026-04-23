from appState import AppState
from cli import CLI, SimOption
from controller import WiredController, GPSController
from robot import Robot
from world import World

def main() -> None:
	appState = AppState()
	world = World(appState)
	robot = Robot()
	cli = CLI()

	cli.startApplication(appState)

	# Sets controller based on CLI input, defaults to WiredController if no valid option is selected.
	if appState.simulation_option == SimOption.GPS.key:
		controller = GPSController()
		print("Startar " + SimOption.GPS.label)
	else:
		controller = WiredController() 
		print("Startar " + SimOption.WIRED.label)

	obstacle_status = "Ja" if appState.has_obstacles else "Nej"
	print("Hinder aktiverade: " + obstacle_status)
	
	world.run_simulation(robot, controller)


if __name__ == "__main__":
	main()