import random
from math import cos, radians, sin
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
	def next_position(self, robot: "Robot", distance: float) -> tuple[float, float]:
		angle = radians(robot.heading)
		next_x = robot.x + cos(angle) * distance
		next_y = robot.y + sin(angle) * distance
		return next_x, next_y

	def step(self, robot: "Robot", world: "LawnWorld") -> None:
		next_x, next_y = self.next_position(robot, robot.move_distance)
		if not robot.move_forward(world, next_x, next_y):
			robot.heading = random.randint(0, 360)
			return

class WireController:
	def step(self, robot: "Robot", world: "LawnWorld") -> None:
		# Placeholder for future wire-following logic.
		return
