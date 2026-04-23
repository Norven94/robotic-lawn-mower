from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import settings

if TYPE_CHECKING:
	from world import World

@dataclass
class Robot:
	x: float = settings.ROBOT_START_X
	y: float = settings.ROBOT_START_Y
	heading: float = settings.ROBOT_START_HEADING
	move_distance: float = settings.MOVE_DISTANCE
	diameter: float = settings.ROBOT_DIAMETER
	# We can use this to turn off the robot once we know when it's 
    # done with the entire lawn.
	is_active: bool = field(default=True, init=False)

	@property
	def position(self) -> tuple[float, float]:
		return (self.x, self.y)

    # Function to move the robot forward, returns False if it can't 
    # move to the next position (e.g. due to boundary), True otherwise
    # This allows the autonomous_step function to decide when to turn 
    # vs move. It also lets the lawn world know that the robot has mowed
    # at the new position, which is important for the visualization. 
	def move_forward(self, world: "World", next_x: float, next_y: float) -> bool:
		if not self.is_active:
			return False
		if not world.is_inside(next_x, next_y, padding=settings.ROBOT_SIZE):
			return False

		self.x = next_x
		self.y = next_y
		world.mark_mowed(self.x, self.y)
		return True
