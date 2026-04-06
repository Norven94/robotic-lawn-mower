from appState import AppState
from controller import RandomController, WireController
from robot import Robot
from world import LawnWorld


def main() -> None:
	appState = AppState()
	world = LawnWorld()
	robot = Robot()

	# We can replace this with CLI selection later.
	controller = RandomController()
	# controller = WireController()

	world.run_simulation(robot, controller)


if __name__ == "__main__":
	main()