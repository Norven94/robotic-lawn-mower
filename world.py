from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, radians, sin
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle

import settings

if TYPE_CHECKING:
	from controller import Controller
	from robot import Robot

@dataclass
class LawnWorld:
	min_x: float = settings.LAWN_MIN_X
	max_x: float = settings.LAWN_MAX_X
	min_y: float = settings.LAWN_MIN_Y
	max_y: float = settings.LAWN_MAX_Y
	mowed_points: list[tuple[float, float]] = field(default_factory=list, init=False)

	# Helper function to check if a coordinate is within the lawn 
	# boundaries, with padding for the robot's radius
	def is_inside(self, x: float, y: float, padding: float = 0.0) -> bool:
		return (
			self.min_x + padding <= x <= self.max_x - padding
			and self.min_y + padding <= y <= self.max_y - padding
		)

	# Adds a coordinate as mowed, which is used for visualization. 
	def mark_mowed(self, x: float, y: float) -> None:
		point = (round(x, 2), round(y, 2))
		if not self.mowed_points or self.mowed_points[-1] != point:
			self.mowed_points.append(point)

	# Main simulation loop, which also handles visualization using 
	# Matplotlib. It utilizes FuncAnimation to update the robot's 
	# position and the mowed path in real-time.
	def run_simulation(self, robot: "Robot", controller: "Controller") -> None:
		self.mark_mowed(robot.x, robot.y)

		figure, axis = plt.subplots(figsize=settings.FIGURE_SIZE)
		axis.set_xlim(self.min_x, self.max_x)
		axis.set_ylim(self.min_y, self.max_y)
		axis.set_title("Lets add robot name from CLI here")
		axis.set_facecolor(settings.LAWN_COLOR)

		# Prepares visual elements to show where the robot has mowed
		# and where the robot currently is.
		path_line = Line2D(
			[],
			[],
			color=settings.PATH_COLOR,
			linewidth=15,
			solid_capstyle="round",
			solid_joinstyle="round",
			zorder=1,
		)
		robot_patch = Circle((robot.x, robot.y), radius=robot.radius, color=settings.ROBOT_COLOR, zorder=3)
		axis.add_patch(robot_patch)
		axis.add_line(path_line)

		# This function is called by FuncAnimation during each frame.
		# It updates the robot's position based on the controllers 
		# logic and updates the visualization accordingly.
		def update(_: int):
			controller.step(robot, self)

			# Update the path line with the new mowed coordinates
			x_values = [point[0] for point in self.mowed_points]
			y_values = [point[1] for point in self.mowed_points]
			path_line.set_data(x_values, y_values)

			robot_patch.center = robot.position

			return path_line, robot_patch


		animation = FuncAnimation(
			figure,
			update,
			frames=None,
			interval=settings.ANIMATION_INTERVAL_MS,
			cache_frame_data=False,
			blit=False,
			repeat=False,
		)

		plt.show()
