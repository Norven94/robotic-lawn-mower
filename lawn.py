from dataclasses import dataclass, field

from matplotlib.patches import Rectangle

import settings

@dataclass
class Lawn:
    min_x: float = settings.LAWN_MIN_X
    max_x: float = settings.LAWN_MAX_X
    min_y: float = settings.LAWN_MIN_Y
    max_y: float = settings.LAWN_MAX_Y

    def is_hitting(self, x: float, y: float, padding: float = 0.0) -> bool:
        return (
            self.min_x + padding <= x <= self.max_x - padding
            and self.min_y + padding <= y <= self.max_y - padding
        )

    def getPatches(self) -> tuple[Rectangle, Rectangle]:
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
        return lawn_boundary, allowed_boundary