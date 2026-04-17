import random
from collections import deque
from dataclasses import dataclass, field
from math import cos, radians, sin
from typing import TYPE_CHECKING, Protocol

import settings

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

class WiredController:
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

@dataclass
class CleanupZone:
	cleanup_origin: tuple[float, float]
	cleanup_full_length: float
	need_cleanup_in_cleanup: bool = False
	cleanup: list["CleanupZone"] = field(default_factory=list)
	x_min: float = 0.0
	x_max: float = 0.0
	horizontal_direction: float = 1.0
	vertical_direction: float = -1.0
	walk_before_turn: float = 0.0
	phase: str = "enter"
	pending_x_min: float | None = None
	pending_x_max: float | None = None

class GPSController:
	def __init__(self) -> None:
		self.phase = "seek_down"
		self.horizontal_direction = 1.0
		self.walk_before_turn = 0.0
		self.need_cleanup = False
		self.default_full_length = settings.LAWN_MAX_X
		self.cleanup: list[CleanupZone] = []
		self.root_x_min = 0.0
		self.root_x_max = settings.LAWN_MAX_X
		self.pending_x_min: float | None = None
		self.pending_x_max: float | None = None
		self.return_path: deque[tuple[float, float]] = deque()
		self.path_mode: str | None = None

	def step(self, robot: "Robot", world: "World") -> None:
		if not robot.is_active:
			return

		if self.return_path:
			self._follow_return_path(robot, world)
			return

		if self.phase == "seek_down":
			next_x = robot.x
			next_y = robot.y - robot.move_distance
			if robot.move_forward(world, next_x, next_y):
				return

			self.phase = "seek_left"
			return

		if self.phase == "seek_left":
			next_x = robot.x - robot.move_distance
			next_y = robot.y
			if robot.move_forward(world, next_x, next_y):
				return

			self._set_root_bounds(robot, world)
			self.horizontal_direction = 1.0
			self.phase = "sweep"
			return

		self.default_walk(robot, world)

	def default_walk(self, robot: "Robot", world: "World") -> None:
		current_phase = self._current_phase()
		if current_phase in {"enter", "move_up"}:
			self._move_vertical(robot, world, flip_direction=current_phase == "move_up")
			return

		direction = self._current_horizontal_direction()
		x_min, x_max = self._current_bounds()
		next_x = self._round_value(robot.x + direction * robot.move_distance)
		if x_min <= next_x <= x_max and robot.move_forward(world, next_x, robot.y):
			self._add_walk_before_turn(robot.move_distance)
			return

		full_row = self._current_walk_before_turn() >= self._current_full_length() - 1e-9
		if not full_row:
			segment = self._find_cleanup_segment(robot, world, direction)
			if segment is not None:
				self._remember_cleanup_segment(segment)

		if full_row and self._current_need_cleanup():
			self._create_cleanup(robot, world)
			return

		self._set_current_phase("move_up")
		self._move_vertical(robot, world, flip_direction=True)

	def find_origin(
		self,
		start: tuple[float, float],
		origin: tuple[float, float],
		world: "World",
	) -> list[tuple[float, float]]:
		if start == origin:
			return [start]

		visited_points = {self._round_point(point) for point in world.mowed_points}
		visited_points.add(start)
		visited_points.add(origin)
		queue: deque[tuple[float, float]] = deque([start])
		parents: dict[tuple[float, float], tuple[float, float] | None] = {start: None}

		while queue:
			current = queue.popleft()
			for neighbor in self._path_neighbors(current, visited_points):
				if neighbor in parents:
					continue
				parents[neighbor] = current
				if neighbor == origin:
					return self._reconstruct_path(parents, origin)
				queue.append(neighbor)

		return [start]

	def _follow_return_path(self, robot: "Robot", world: "World") -> None:
		next_x, next_y = self.return_path[0]
		if not robot.move_forward(world, next_x, next_y):
			robot.is_active = False
			return

		self.return_path.popleft()
		if self.return_path:
			return

		if self.path_mode == "return" and self.cleanup:
			self.cleanup.pop()

		self.path_mode = None

	def _move_vertical(self, robot: "Robot", world: "World", flip_direction: bool) -> None:
		current_phase = self._current_phase()
		previous_direction = self._current_horizontal_direction()
		vertical_direction = self._current_vertical_direction()
		next_y = self._round_value(robot.y + vertical_direction * robot.move_distance)
		next_point = (self._round_value(robot.x), next_y)
		was_visited = next_point in self._visited_points(world)

		if self.cleanup and was_visited and current_phase != "enter":
			self._start_cleanup_return(robot, world)
			return

		if not robot.move_forward(world, robot.x, next_y):
			if self.cleanup:
				self._start_cleanup_return(robot, world)
				return

			robot.is_active = False
			return

		self._set_walk_before_turn(0.0)
		if current_phase == "enter" and was_visited:
			return

		fallback_direction = -previous_direction if flip_direction else previous_direction
		self._set_horizontal_direction(self._choose_row_direction(robot, world, fallback_direction))
		self._set_current_phase("sweep")

	def _start_cleanup_return(self, robot: "Robot", world: "World") -> None:
		if not self.cleanup:
			return

		origin = self.cleanup[-1].cleanup_origin
		path = self.find_origin(self._round_point(robot.position), origin, world)
		if len(path) == 1:
			if path[0] != origin:
				robot.is_active = False
				return
			self.cleanup.pop()
			return

		self.return_path = deque(path[1:])
		self.path_mode = "return"

	def _create_cleanup(self, robot: "Robot", world: "World") -> None:
		segment = self._consume_pending_segment()
		if segment is None:
			self._set_current_need_cleanup(False)
			self._set_current_phase("move_up")
			return

		x_min, x_max = segment
		if x_max <= x_min:
			self._set_current_need_cleanup(False)
			self._set_current_phase("move_up")
			return

		self._set_current_need_cleanup(False)
		self._set_current_phase("move_up")
		entry_x = x_min if abs(robot.x - x_min) <= abs(robot.x - x_max) else x_max
		start_direction = 1.0 if entry_x == x_min else -1.0
		cleanup_zone = CleanupZone(
			cleanup_origin=self._round_point(robot.position),
			cleanup_full_length=self._round_value(x_max - x_min),
			x_min=x_min,
			x_max=x_max,
			horizontal_direction=start_direction,
			vertical_direction=-self._current_vertical_direction(),
		)
		if self.cleanup:
			self.cleanup[-1].cleanup.append(cleanup_zone)
		self.cleanup.append(cleanup_zone)

		entry_point = (self._round_value(entry_x), self._round_value(robot.y))
		if entry_point != self._round_point(robot.position):
			path = self.find_origin(self._round_point(robot.position), entry_point, world)
			self.return_path = deque(path[1:])
			self.path_mode = "entry"

	def _set_root_bounds(self, robot: "Robot", world: "World") -> None:
		self.root_x_min = self._round_value(robot.x)
		probe_x = self.root_x_min
		while True:
			next_x = self._round_value(probe_x + robot.move_distance)
			if not world.lawn.is_hitting(next_x, robot.y, padding=settings.ROBOT_SIZE):
				break
			probe_x = next_x
		self.root_x_max = probe_x
		self.default_full_length = self._round_value(self.root_x_max - self.root_x_min)

	def _find_cleanup_segment(
		self,
		robot: "Robot",
		world: "World",
		direction: float,
	) -> tuple[float, float] | None:
		x_min, x_max = self._current_bounds()
		x = self._round_value(robot.x + direction * robot.move_distance)
		first: float | None = None
		last: float | None = None

		while x_min <= x <= x_max:
			if world.is_inside(x, robot.y, padding=settings.ROBOT_SIZE):
				if first is None:
					first = x
				last = x
			elif first is not None:
				break
			x = self._round_value(x + direction * robot.move_distance)

		if first is None or last is None:
			return None

		return (min(first, last), max(first, last))

	def _remember_cleanup_segment(self, segment: tuple[float, float]) -> None:
		x_min, x_max = segment
		if self.cleanup:
			current = self.cleanup[-1]
			current.need_cleanup_in_cleanup = True
			current.pending_x_min = x_min if current.pending_x_min is None else min(current.pending_x_min, x_min)
			current.pending_x_max = x_max if current.pending_x_max is None else max(current.pending_x_max, x_max)
			return

		self.need_cleanup = True
		self.pending_x_min = x_min if self.pending_x_min is None else min(self.pending_x_min, x_min)
		self.pending_x_max = x_max if self.pending_x_max is None else max(self.pending_x_max, x_max)

	def _consume_pending_segment(self) -> tuple[float, float] | None:
		if self.cleanup:
			current = self.cleanup[-1]
			if current.pending_x_min is None or current.pending_x_max is None:
				return None
			segment = (current.pending_x_min, current.pending_x_max)
			current.pending_x_min = None
			current.pending_x_max = None
			current.need_cleanup_in_cleanup = False
			return segment

		if self.pending_x_min is None or self.pending_x_max is None:
			return None
		segment = (self.pending_x_min, self.pending_x_max)
		self.pending_x_min = None
		self.pending_x_max = None
		return segment

	def _current_phase(self) -> str:
		if self.cleanup:
			return self.cleanup[-1].phase
		return self.phase

	def _set_current_phase(self, phase: str) -> None:
		if self.cleanup:
			self.cleanup[-1].phase = phase
			return
		self.phase = phase

	def _current_horizontal_direction(self) -> float:
		if self.cleanup:
			return self.cleanup[-1].horizontal_direction
		return self.horizontal_direction

	def _set_horizontal_direction(self, direction: float) -> None:
		if self.cleanup:
			self.cleanup[-1].horizontal_direction = direction
			return
		self.horizontal_direction = direction

	def _current_walk_before_turn(self) -> float:
		if self.cleanup:
			return self.cleanup[-1].walk_before_turn
		return self.walk_before_turn

	def _add_walk_before_turn(self, distance: float) -> None:
		self._set_walk_before_turn(self._current_walk_before_turn() + distance)

	def _set_walk_before_turn(self, value: float) -> None:
		value = self._round_value(value)
		if self.cleanup:
			self.cleanup[-1].walk_before_turn = value
			return
		self.walk_before_turn = value

	def _current_full_length(self) -> float:
		if self.cleanup:
			return self.cleanup[-1].cleanup_full_length
		return self.default_full_length

	def _current_need_cleanup(self) -> bool:
		if self.cleanup:
			return self.cleanup[-1].need_cleanup_in_cleanup
		return self.need_cleanup

	def _set_current_need_cleanup(self, value: bool) -> None:
		if self.cleanup:
			self.cleanup[-1].need_cleanup_in_cleanup = value
			return
		self.need_cleanup = value

	def _current_bounds(self) -> tuple[float, float]:
		if self.cleanup:
			return self.cleanup[-1].x_min, self.cleanup[-1].x_max
		return self.root_x_min, self.root_x_max

	def _choose_row_direction(self, robot: "Robot", world: "World", fallback_direction: float) -> float:
		x_min, x_max = self._current_bounds()
		if abs(robot.x - x_min) < 1e-9 or abs(robot.x - x_max) < 1e-9:
			return fallback_direction

		left_edge = self._round_value(robot.x)
		right_edge = self._round_value(robot.x)

		while True:
			next_left = self._round_value(left_edge - robot.move_distance)
			if next_left < x_min or not world.is_inside(next_left, robot.y, padding=settings.ROBOT_SIZE):
				break
			left_edge = next_left

		while True:
			next_right = self._round_value(right_edge + robot.move_distance)
			if next_right > x_max or not world.is_inside(next_right, robot.y, padding=settings.ROBOT_SIZE):
				break
			right_edge = next_right

		left_span = self._round_value(robot.x - left_edge)
		right_span = self._round_value(right_edge - robot.x)
		if right_span > left_span:
			return 1.0
		if left_span > right_span:
			return -1.0
		return fallback_direction

	def _current_vertical_direction(self) -> float:
		if self.cleanup:
			return self.cleanup[-1].vertical_direction
		return 1.0

	def _path_neighbors(
		self,
		point: tuple[float, float],
		allowed: set[tuple[float, float]],
	) -> list[tuple[float, float]]:
		x, y = point
		neighbors: list[tuple[float, float]] = []
		for move_x, move_y in ((self.default_step(), 0.0), (-self.default_step(), 0.0), (0.0, self.default_step()), (0.0, -self.default_step())):
			candidate = (self._round_value(x + move_x), self._round_value(y + move_y))
			if candidate in allowed:
				neighbors.append(candidate)
		return neighbors

	def _reconstruct_path(
		self,
		parents: dict[tuple[float, float], tuple[float, float] | None],
		goal: tuple[float, float],
	) -> list[tuple[float, float]]:
		path = [goal]
		current: tuple[float, float] | None = goal
		while current is not None and parents[current] is not None:
			current = parents[current]
			if current is None:
				break
			path.append(current)
		path.reverse()
		return path

	def _visited_points(self, world: "World") -> set[tuple[float, float]]:
		return {self._round_point(point) for point in world.mowed_points}

	def default_step(self) -> float:
		return settings.MOVE_DISTANCE

	def _round_point(self, point: tuple[float, float]) -> tuple[float, float]:
		return (self._round_value(point[0]), self._round_value(point[1]))

	def _round_value(self, value: float) -> float:
		return round(value, 2)


