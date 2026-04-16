from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle

import appState
from lawn import Lawn
from utilities import getLawnPoints, sync_linewidth_to_data, LawnPointsOption

import settings 
from obstacles import rectangleobstacles

if TYPE_CHECKING:
	from controller import Controller
	from robot import Robot

@dataclass
class World:
	# min_x: float = settings.LAWN_MIN_X
	# max_x: float = settings.LAWN_MAX_X
	# min_y: float = settings.LAWN_MIN_Y
	# max_y: float = settings.LAWN_MAX_Y
	lawn = Lawn()
	
	mowed_points: list[tuple[float, float]] = field(default_factory=list, init=False)
	obstacles: list = field(default_factory=list, init=False)

	#List for obstacles
	def __post_init__ (self):
		house = rectangleobstacles( settings.OFF_SET_PLOT_X, settings.OFF_SET_PLOT_Y, settings.HOUSE_SIZE )
		self.obstacles.append(house)

	# Helper function to check if a coordinate is within the lawn 
	# boundaries, with padding for the robot's size.
	# Obstacles on lawn
	def is_inside(self, x: float, y: float, padding: float = 0.0) -> bool:
		valid_path = True
		#Check if robot is on lawn
		valid_path = self.lawn.is_hitting(x, y, padding)
		for obstacle in self.obstacles:
			if obstacle.is_hitting(x, y, padding):
				valid_path = False
			
		return valid_path

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

		axis.set_xlim(self.lawn.min_x, self.lawn.max_x)
		axis.set_ylim(self.lawn.min_y, self.lawn.max_y)
		axis.set_aspect("equal", adjustable="box")
		axis.set_title("Lets add robot name from CLI here")
		axis.set_facecolor(settings.LAWN_COLOR)

		lawn_boundary, allowed_boundary = self.lawn.getPatches()
		axis.add_patch(lawn_boundary)
		axis.add_patch(allowed_boundary)

		for obstacle in self.obstacles:
			renderd_obstacle = Rectangle(
				(obstacle.x, obstacle.y),
				obstacle.width,
				obstacle.height,
				fill=True,
				facecolor=settings.HOUSE_COLOR,
				edgecolor= "black",
				linewidth=2,
				zorder=2, 
			)
			obstacle_border = Rectangle(
				(obstacle.x - settings.ROBOT_SIZE, obstacle.y - settings.ROBOT_SIZE),
				obstacle.width + settings.ROBOT_SIZE * 2,
				obstacle.height + settings.ROBOT_SIZE * 2,
				fill=False,
				edgecolor=settings.BOUNDARY_COLOR,
  			    linewidth=2,
  			    linestyle="--",
  			    zorder=2,
			)
			axis.add_patch(renderd_obstacle)
			axis.add_patch(obstacle_border)

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
		
		time_legend = axis.text(0.03,0.95, f"Tid:{appState.time}", transform=axis.transAxes, fontsize=12,fontweight='bold', bbox=dict(facecolor='white',alpha=0.5))
		goal_points = getLawnPoints(self.lawn.max_x, self.lawn.min_x, self.lawn.max_y, self.lawn.min_y, LawnPointsOption.TESTING)

		# This function is called by FuncAnimation during each frame.
		# It updates the robot's position based on the controllers 
		# logic and updates the visualization accordingly.
		def update(_: int):
			appState.time += settings.MOVE_DISTANCE/settings.ROBOT_REAL_SPEED_MPS
			#Kolla alla unika punkter
			amount_mowed = len(set(self.mowed_points))

			#Kollar om man nått målet, dvs 95% av gräsmattan klippt. Om så är fallet, stoppa roboten och skriv ut att klippningen är klar.
			if amount_mowed >= goal_points and robot.is_active:
				robot.is_active = False #Stängs av
				print("Klippningen är klar!")
				#Stoppa renderingen direkt när roboten stängs av
				animation.event_source.stop()

			if robot.is_active:
				controller.step(robot, self)

			# Update the path line with the new mowed coordinates
			x_values = [point[0] for point in self.mowed_points]
			y_values = [point[1] for point in self.mowed_points]
			path_line.set_data(x_values, y_values)

			robot_patch.center = robot.position
			
			time_legend.set_text(f"Tid: {appState.time:.1f} s")

			return path_line, robot_patch, time_legend

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