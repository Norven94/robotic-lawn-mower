from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle

from lawn import Lawn
from utilities import getLawnPoints, sync_linewidth_to_data, LawnPointsOption, get_milestone_goals, log_milestone_result, save_simulation_results

import settings 
from obstacles import Obstacles

if TYPE_CHECKING:
	from controller import Controller
	from robot import Robot
	from appState import AppState

@dataclass
class World:
	appState: "AppState"
	lawn = Lawn()
	obstacles = Obstacles()
	mowed_points: list[tuple[float, float]] = field(default_factory=list, init=False)
	goal_points = getLawnPoints(lawn.max_x, lawn.min_x, lawn.max_y, lawn.min_y, LawnPointsOption.TESTING)
	milestones_track = [
		LawnPointsOption.TESTING,
		LawnPointsOption.FIFTY,
		LawnPointsOption.SEVENTY,
		LawnPointsOption.NINETY,
		LawnPointsOption.NINETYFIVE,
	]

	# Helper function to check if a coordinate is within the lawn 
	# boundaries, with padding for the robot's size. It also checks if the coordinate is colliding with any obstacles.
	def is_inside(self, x: float, y: float, padding: float = 0.0) -> bool:
		valid_path = True
		#Check if robot is on lawn
		valid_path = self.lawn.is_hitting(x, y, padding)
		for obstacle in self.obstacles.all_obstacles:
			if obstacle.is_hitting(x, y, padding):
				valid_path = False
		
		is_hitting_something = not valid_path
		if is_hitting_something:
				self.appState.collisions += 1

		if self.appState.has_obstacles:
			for obstacle in self.obstacles.all_obstacles:
				if obstacle.is_hitting(x, y, padding):
					valid_path = False
					break
			
		return valid_path

	# Adds a coordinate as mowed, which is used for visualization. 
	def mark_mowed(self, x: float, y: float) -> None:
		point = (round(x, 2), round(y, 2))
		if not self.mowed_points or self.mowed_points[-1] != point:
			self.mowed_points.append(point)

	# This function sets up all static elements in the simulation like the lawn boundaries and obstacles. 
	# It is called once at the beginning of the simulation.
	def create_garden(self, axis: Axes):
		axis.set_xlim(self.lawn.min_x, self.lawn.max_x)
		axis.set_ylim(self.lawn.min_y, self.lawn.max_y)
		axis.set_aspect("equal", adjustable="box")
		axis.set_title("Simulering av robotgräsklipparen: " + self.appState.robot_name)
		axis.set_facecolor(settings.LAWN_COLOR)

		lawn_boundary, allowed_boundary = self.lawn.getPatches()
		axis.add_patch(lawn_boundary)
		axis.add_patch(allowed_boundary)

		if self.appState.has_obstacles:
			obstacle_boundaries = self.obstacles.getPatches()
			for obstacle in obstacle_boundaries:
				axis.add_patch(obstacle)

	def setup_simulation(self, robot: "Robot") -> list[float]:
		self.mark_mowed(robot.x, robot.y)
		return get_milestone_goals(self.lawn, self.milestones_track)

	def step_simulation(self, robot: "Robot", controller: "Controller", milestone_goals: list[float]) -> bool:
		self.appState.time += settings.MOVE_DISTANCE / settings.ROBOT_REAL_SPEED_MPS
		amount_mowed = len(set(self.mowed_points))

		self.appState.distance += settings.MOVE_DISTANCE

		for milestone_option, sub_goal in zip(self.milestones_track, milestone_goals):
			log_milestone_result(milestone_option.value, sub_goal, amount_mowed, self.appState)

		if amount_mowed >= self.goal_points and robot.is_active:
			robot.is_active = False
			print("Klippningen är klar!")

		if robot.is_active:
			controller.step(robot, self)

		return robot.is_active

	def finalize_simulation(self) -> None:
		print("Här är all statistik")
		print(self.appState.results)
		result_path = save_simulation_results(self.appState)
		print(f"Resultat sparade i {result_path}")

	# Main simulation loop, which also handles visualization using 
	# Matplotlib. It utilizes FuncAnimation to update the robot's 
	# position and the mowed path in real-time.
	def run_simulation(self, robot: "Robot", controller: "Controller", animate: bool = True) -> None:
		milestone_goals = self.setup_simulation(robot)

		if not animate:
			while robot.is_active:
				self.step_simulation(robot, controller, milestone_goals)

			self.finalize_simulation()
			return

		figure, axis = plt.subplots(figsize=settings.FIGURE_SIZE)
		self.create_garden(axis)
		time_legend = axis.text(0.03,0.95, f"Tid:{self.appState.time}", transform=axis.transAxes, fontsize=12,fontweight='bold', bbox=dict(facecolor='white',alpha=0.5))
		length_legend = axis.text(0.03,0.90, f"Sträcka:{self.appState.distance}", transform=axis.transAxes, fontsize=12,fontweight='bold', bbox=dict(facecolor='white',alpha=0.5))
		collision_legend = axis.text(0.03,0.85, f"Antal kollisioner:{self.appState.collisions}", transform=axis.transAxes, fontsize=12,fontweight='bold', bbox=dict(facecolor='white',alpha=0.5))

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
			if not self.step_simulation(robot, controller, milestone_goals):
				animation.event_source.stop()

			# Update the path line with the new mowed coordinates
			x_values = [point[0] for point in self.mowed_points]
			y_values = [point[1] for point in self.mowed_points]
			path_line.set_data(x_values, y_values)

			robot_patch.center = robot.position
			
			time_legend.set_text(f"Tid: {self.appState.time:.1f} s")
			length_legend.set_text(f"Sträcka: {self.appState.distance:.1f} m")
			collision_legend.set_text(f"Antal kollisioner: {self.appState.collisions}")

			return path_line, robot_patch, time_legend, length_legend, collision_legend

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
		self.finalize_simulation()