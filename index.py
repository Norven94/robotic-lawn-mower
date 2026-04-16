from appState import AppState
from cli import CLI, SimOption
from controller import RandomController, WireController
from robot import Robot
from world import LawnWorld


def main() -> None:
	appState = AppState()
	world = LawnWorld()
	robot = Robot()
	cli = CLI()
	appState.simulation_option = cli.startApplication()

	# We can replace this with CLI selection later.
	print(appState.simulation_option)
	if appState.simulation_option == SimOption.GPS.key:
		controller = RandomController()
	elif appState.simulation_option == SimOption.WIRED.key:
		controller = WireController()
	else:
		controller = RandomController()  # Default to RandomController if no valid option is selected

	world.run_simulation(robot, controller)


if __name__ == "__main__":
	main()