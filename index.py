from appState import AppState
import appState
from cli import CLI, SimOption
from controller import WiredController, GPSController
from robot import Robot
from world import World
import world


def main() -> None:
	appState = AppState()
	world = World()
	robot = Robot()
	cli = CLI()
	appState.simulation_option = cli.startApplication(appState)
        
	if "_yes" in appState.simulation_option:
		appState.has_obstacles = True
	else:
		appState.has_obstacles = False

	# Sets controller based on CLI input, defaults to WiredController if no valid option is selected.
	if appState.simulation_option == SimOption.GPS_NO.key:
		controller = GPSController()
	elif appState.simulation_option == SimOption.GPS_YES.key:
		controller = GPSController()
	elif appState.simulation_option == SimOption.WIRED_NO.key:
		controller = WiredController()
	elif appState.simulation_option == SimOption.WIRED_YES.key:
		controller = WiredController()
	else:
		controller = WiredController() 

	print("Hinder kommer att finnas i trädgården: " + str(appState.has_obstacles))
	
	world.run_simulation(robot, controller, appState)


if __name__ == "__main__":
	main()