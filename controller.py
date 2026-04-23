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

# Stores the same sweep state as the root walk, but for one nested cleanup area.
@dataclass
class CleanupZone:
	cleanup_origin: tuple[float, float]
	cleanup_full_length: float
	cleanup: list["CleanupZone"] = field(default_factory=list)
	# Fixed side of the origin that belongs to this cleanup zone.
	cleanup_direction: float = -1.0
	# Current left/right sweep direction for the active row.
	horizontal_direction: float = -1.0
	# Direction used when stepping between rows in this zone.
	vertical_direction: float = -1.0
	walk_before_turn: float = 0.0
	phase: str = "enter"
	pending_cleanup_length: float | None = None
	pending_direction: float | None = None

class GPSController:
	def __init__(self) -> None:
		# Initializes one root sweep state and a stack of nested cleanup zones.
		self.phase = "seek_down"
		self.horizontal_direction = 1.0
		self.walk_before_turn = 0.0
		# Root full length. Cleanup zones provide their own full length via CleanupZone.
		self.default_full_length = settings.LAWN_MAX_X
		self.cleanup: list[CleanupZone] = []
		self.root_x_min = 0.0
		self.root_x_max = settings.LAWN_MAX_X
		self.pending_cleanup_length: float | None = None
		self.pending_direction: float | None = None
		self.return_path: deque[tuple[float, float]] = deque()

	# Runs one controller tick for either setup, sweeping, or returning to an origin.
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

	# Runs the shared serpentine pattern used by both the root sweep and cleanups.
	def default_walk(self, robot: "Robot", world: "World") -> None:

		current_phase = self._current_phase()
		if current_phase in {"enter", "move_up"}:
			self._move_vertical(robot, world)
			return

		direction = self._current_horizontal_direction()
		x_min, x_max = self._current_bounds()
		next_x = self._round_value(robot.x + direction * robot.move_distance)
		if x_min <= next_x <= x_max and robot.move_forward(world, next_x, robot.y):
			self._add_walk_before_turn(robot.move_distance)
			return

		if not (x_min <= next_x <= x_max):
			world.is_inside(next_x, robot.y, padding=settings.ROBOT_SIZE)

		full_row = self._current_walk_before_turn() >= self._current_full_length() - 1e-9
		if not full_row:
			cleanup_length = self._missed_length(robot, world, direction)
			if cleanup_length > 0:
				self._remember_cleanup(cleanup_length, direction)

		if full_row and self._has_pending_cleanup():
			self._create_cleanup(robot)
			return

		self._set_current_phase("move_up")
		self._move_vertical(robot, world)

	# Finds a path through already visited points back to a stored cleanup origin.
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

	# Consumes one step from the queued path back to the current cleanup origin.
	def _follow_return_path(self, robot: "Robot", world: "World") -> None:

		next_x, next_y = self.return_path[0]
		if not robot.move_forward(world, next_x, next_y):
			robot.is_active = False
			return

		self.return_path.popleft()
		if self.return_path:
			return

		if self.cleanup:
			self.cleanup.pop()

	# Moves one row up or down and decides whether a cleanup should continue or return.
	def _move_vertical(self, robot: "Robot", world: "World") -> None:

		current_phase = self._current_phase()
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

		if current_phase != "enter":
			self._set_horizontal_direction(-self._current_horizontal_direction())
		self._set_current_phase("sweep")

	# Queues a path back to the active cleanup origin once that cleanup is done.
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

	# Pushes a child cleanup zone once a full row confirms a missed area exists.
	def _create_cleanup(self, robot: "Robot") -> None:

		pending_cleanup = self._consume_pending_cleanup()
		if pending_cleanup is None:
			self._set_current_phase("move_up")
			return

		cleanup_length, pending_direction = pending_cleanup
		if cleanup_length <= 0:
			self._set_current_phase("move_up")
			return

		self._set_current_phase("move_up")
		cleanup_zone = CleanupZone(
			cleanup_origin=self._round_point(robot.position),
			cleanup_full_length=cleanup_length,
			cleanup_direction=-pending_direction,
			horizontal_direction=-pending_direction,
			vertical_direction=-self._current_vertical_direction(),
		)
		if self.cleanup:
			self.cleanup[-1].cleanup.append(cleanup_zone)
		self.cleanup.append(cleanup_zone)

	# Captures the left and right lawn limits for the root sweep only.
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

	# Measures the next reachable straight segment after a blocked row ends early.
	def _missed_length(
		self,
		robot: "Robot",
		world: "World",
		direction: float,
	) -> float:

		x_min, x_max = self._current_bounds()
		x = self._round_value(robot.x + direction * robot.move_distance)
		first: float | None = None
		last: float | None = None

		while x_min <= x <= x_max:
			if world.is_inside(x, robot.y, padding=settings.ROBOT_SIZE, record_collision=False):
				if first is None:
					first = x
				last = x
			elif first is not None:
				break
			x = self._round_value(x + direction * robot.move_distance)

		if first is None or last is None:
			return 0.0

		return self._round_value(abs(last - first))

	# Stores one pending cleanup for the active sweep level.
	def _remember_cleanup(self, cleanup_length: float, direction: float) -> None:

		if self.cleanup:
			current = self.cleanup[-1]
			current.pending_cleanup_length = cleanup_length if current.pending_cleanup_length is None else max(current.pending_cleanup_length, cleanup_length)
			current.pending_direction = direction
			return

		self.pending_cleanup_length = cleanup_length if self.pending_cleanup_length is None else max(self.pending_cleanup_length, cleanup_length)
		self.pending_direction = direction

	# Removes and returns the pending cleanup for the active sweep level.
	def _consume_pending_cleanup(self) -> tuple[float, float] | None:

		if self.cleanup:
			current = self.cleanup[-1]
			if current.pending_cleanup_length is None or current.pending_direction is None:
				return None
			cleanup = (current.pending_cleanup_length, current.pending_direction)
			current.pending_cleanup_length = None
			current.pending_direction = None
			return cleanup

		if self.pending_cleanup_length is None or self.pending_direction is None:
			return None
		cleanup = (self.pending_cleanup_length, self.pending_direction)
		self.pending_cleanup_length = None
		self.pending_direction = None
		return cleanup

	# Returns the phase for the active sweep level.
	def _current_phase(self) -> str:

		if self.cleanup:
			return self.cleanup[-1].phase
		return self.phase

	# Writes the phase for the active sweep level.
	def _set_current_phase(self, phase: str) -> None:

		if self.cleanup:
			self.cleanup[-1].phase = phase
			return
		self.phase = phase

	# Returns the current row direction for the active sweep level.
	def _current_horizontal_direction(self) -> float:

		if self.cleanup:
			return self.cleanup[-1].horizontal_direction
		return self.horizontal_direction

	# Writes the row direction for the active sweep level.
	def _set_horizontal_direction(self, direction: float) -> None:

		if self.cleanup:
			self.cleanup[-1].horizontal_direction = direction
			return
		self.horizontal_direction = direction

	# Returns how far the active sweep has walked on the current row.
	def _current_walk_before_turn(self) -> float:

		if self.cleanup:
			return self.cleanup[-1].walk_before_turn
		return self.walk_before_turn

	# Accumulates walked distance for the current row.
	def _add_walk_before_turn(self, distance: float) -> None:

		self._set_walk_before_turn(self._current_walk_before_turn() + distance)

	# Resets or updates the current-row distance counter for the active sweep.
	def _set_walk_before_turn(self, value: float) -> None:

		value = self._round_value(value)
		if self.cleanup:
			self.cleanup[-1].walk_before_turn = value
			return
		self.walk_before_turn = value

	# Returns the target full row length for the active sweep level.
	def _current_full_length(self) -> float:

		if self.cleanup:
			return self.cleanup[-1].cleanup_full_length
		return self.default_full_length

	# Checks whether the active sweep level has remembered a missed area.
	def _has_pending_cleanup(self) -> bool:

		if self.cleanup:
			current = self.cleanup[-1]
			return current.pending_cleanup_length is not None and current.pending_direction is not None
		return self.pending_cleanup_length is not None and self.pending_direction is not None

	# Returns the horizontal bounds for the active sweep level.
	def _current_bounds(self) -> tuple[float, float]:

		if self.cleanup:
			current = self.cleanup[-1]
			if current.cleanup_direction < 0:
				return (
					self._round_value(current.cleanup_origin[0] - current.cleanup_full_length),
					current.cleanup_origin[0],
				)
			return (
				current.cleanup_origin[0],
				self._round_value(current.cleanup_origin[0] + current.cleanup_full_length),
			)
		return self.root_x_min, self.root_x_max

	# Returns the row-to-row movement direction for the active sweep level.
	def _current_vertical_direction(self) -> float:

		if self.cleanup:
			return self.cleanup[-1].vertical_direction
		return 1.0

	# Returns grid neighbors used by find_origin when backtracking to an origin.
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

	# Builds the final path once find_origin reaches its target.
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

	# Normalizes the visited coordinates used for cleanup completion checks.
	def _visited_points(self, world: "World") -> set[tuple[float, float]]:

		return {self._round_point(point) for point in world.mowed_points}

	# Returns the grid step size used by both sweeping and origin finding.
	def default_step(self) -> float:

		return settings.MOVE_DISTANCE

	# Rounds a point to the same grid precision used by mowed_points.
	def _round_point(self, point: tuple[float, float]) -> tuple[float, float]:

		return (self._round_value(point[0]), self._round_value(point[1]))

	# Rounds one coordinate to the controller grid precision.
	def _round_value(self, value: float) -> float:

		return round(value, 2)


