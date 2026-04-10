from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle

import settings
from utilities import sync_linewidth_to_data

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
	# boundaries, with padding for the robot's size.
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
		axis.set_aspect("equal", adjustable="box")
		axis.set_title("Lets add robot name from CLI here")
		axis.set_facecolor(settings.LAWN_COLOR)

		# Outer rectangle: full lawn boundary.
		lawn_boundary = Rectangle(
			(self.min_x, self.min_y),
			self.max_x - self.min_x,
			self.max_y - self.min_y,
			fill=False,
			edgecolor="black",
			linewidth=2,
			zorder=2,
		)
		axis.add_patch(lawn_boundary)

		# Inner rectangle: where robot center is allowed to move.
		allowed_min_x = self.min_x + settings.ROBOT_SIZE
		allowed_max_x = self.max_x - settings.ROBOT_SIZE
		allowed_min_y = self.min_y + settings.ROBOT_SIZE
		allowed_max_y = self.max_y - settings.ROBOT_SIZE
		allowed_boundary = Rectangle(
			(allowed_min_x, allowed_min_y),
			allowed_max_x - allowed_min_x,
			allowed_max_y - allowed_min_y,
			fill=False,
			edgecolor=settings.BOUNDARY_COLOR,
			linewidth=2,
			linestyle="--",
			zorder=2,
		)
		axis.add_patch(allowed_boundary)

		# Prepares visual elements to show where the robot has mowed
		# and where the robot currently is.
		path_line = Line2D(
			[],
			[],
			color=settings.PATH_COLOR,
			linewidth=0,
			solid_capstyle="round",
			solid_joinstyle="round",
			zorder=1,
		)
		robot_patch = Circle((robot.x, robot.y), radius=settings.ROBOT_SIZE, color=settings.ROBOT_COLOR, zorder=3)
		axis.add_patch(robot_patch)
		axis.add_line(path_line)

		# The line width is in pixles and needs to be converted to data units so it matches the robot's blade diameter. 
		# We also need to update it on every redraw in case the user resizes the window.
		blade_diameter = robot.diameter
		sync_linewidth_to_data(path_line, figure, axis, blade_diameter)
		figure.canvas.mpl_connect(
			"draw_event",
			lambda _event: sync_linewidth_to_data(path_line, figure, axis, blade_diameter),
		)
		

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
