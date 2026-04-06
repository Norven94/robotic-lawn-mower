import random
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
	from robot import Robot
	from world import LawnWorld


# This is the base type for the controllers, which controller to use
# can be selected in the CLI and passed to the LawnWorld's 
# run_simulation function. This decides how the robot should work and 
# move during the simulation. 
class Controller(Protocol):
	def step(self, robot: "Robot", world: "LawnWorld") -> None:
		...


class RandomController:
	def step(self, robot: "Robot", world: "LawnWorld") -> None:
		if robot.detect_boundary(world):
			robot.heading = random.randint(0, 360)
			return

		robot.move_forward(world)


class WireController:
	def step(self, robot: "Robot", world: "LawnWorld") -> None:
		# Placeholder for future wire-following logic.
		return
