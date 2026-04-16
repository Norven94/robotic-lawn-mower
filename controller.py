import random
from math import cos, radians, sin
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
	from robot import Robot
	from world import World

# This is the base type for the controllers, which controller to use
# can be selected in the CLI and passed to the LawnWorld's 
# run_simulation function. This decides how the robot should work and 
# move during the simulation. 
class Controller(Protocol):
	def step(self, robot: "Robot", world: "World") -> None:
		...

class RandomController:
	def next_position(self, robot: "Robot", distance: float) -> tuple[float, float]:
		angle = radians(robot.heading)
		next_x = robot.x + cos(angle) * distance
		next_y = robot.y + sin(angle) * distance
		return next_x, next_y

	def step(self, robot: "Robot", world: "World") -> None:
		next_x, next_y = self.next_position(robot, robot.move_distance)
		if not robot.move_forward(world, next_x, next_y):
			robot.heading = random.randint(0, 360)
			return

class WireController:
	def __init__(self) -> None:
		self.phase = "seek_down"
		self.horizontal_direction = 1.0

	def step(self, robot: "Robot", world: "World") -> None:
		if not robot.is_active:
			return

		# Move down using fixed-size steps until we hit the boundary.
		if self.phase == "seek_down":
			next_x = robot.x
			next_y = robot.y - robot.move_distance
			if robot.move_forward(world, next_x, next_y):
				return

			self.phase = "seek_left"
			return

		# Move left using fixed-size steps until we hit the boundary.
		if self.phase == "seek_left":
			next_x = robot.x - robot.move_distance
			next_y = robot.y
			if robot.move_forward(world, next_x, next_y):
				return

			self.horizontal_direction = 1.0
			self.phase = "sweep"
			return

		if self.phase == "sweep":
			next_x = robot.x + self.horizontal_direction * robot.move_distance
			next_y = robot.y
			if robot.move_forward(world, next_x, next_y):
				return

			self.phase = "move_up"

		if self.phase == "move_up":
			next_x = robot.x
			next_y = robot.y + robot.move_distance
			if robot.move_forward(world, next_x, next_y):
				self.horizontal_direction *= -1.0
				self.phase = "sweep"
				return

			# Reached top boundary; stop simulation movement.
			robot.is_active = False
