from appState import AppState
from cli import CLI, SimOption
from controller import WiredController, GPSController
from robot import Robot
from world import World


def main() -> None:
	appState = AppState()
	world = World()
	robot = Robot()
	cli = CLI()
	appState.simulation_option = cli.startApplication()

	# We can replace this with CLI selection later.
	print(appState.simulation_option)
	if appState.simulation_option == SimOption.GPS.key:
		controller = GPSController()
	elif appState.simulation_option == SimOption.WIRED.key:
		controller = WiredController()
	else:
		controller = WiredController()  # Default to WiredController if no valid option is selected

	world.run_simulation(robot, controller)


if __name__ == "__main__":
	main()