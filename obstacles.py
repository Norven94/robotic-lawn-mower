#How the obstacles work
#Shape
from dataclasses import dataclass, field
from typing import Protocol

from matplotlib.patches import Circle, Rectangle

import settings

# Base obstacle protocol that defines how all obstacles should be structured. 
# This allows us to easily add new types of obstacles in the future (e.g. circular obstacles) 
# by just creating a new class that implements this protocol.
class Obstacle(Protocol):
    x: float
    y: float
    width: float
    height: float
    type: str
    def is_hitting(self, robot_x, robot_y, padding) -> bool:
        ...

# This is a class to handle all obstacles that should be rendered in the world 
@dataclass
class Obstacles:
    all_obstacles: list[Obstacle] = field(default_factory=list, init=False)

    #List for obstacles
    def __post_init__ (self):
        house = RectangleObstacles( settings.OFF_SET_PLOT_X, settings.OFF_SET_PLOT_Y, settings.HOUSE_SIZE, settings.HOUSE_SIZE )
        self.all_obstacles.append(house)

    # Helper function to setup all obstacle elements for the world to render
    def getPatches(self) -> list[Rectangle | Circle]:
        patches: list[Rectangle | Circle] = []

        for obstacle in self.all_obstacles:
            if obstacle.type == "rectangle":
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
                patches.append(renderd_obstacle)
                patches.append(obstacle_border)
            if obstacle.type == "circle":
                # Add code here to handle rendering of circular elements.
                pass

        return patches

# This is a class to represent rectangular obstacles, which can be used to represent the house in the lawn. 
@dataclass
class RectangleObstacles:
    x: float
    y: float
    width: float
    height: float
    type: str = "rectangle"

    def is_hitting(self, robot_x, robot_y, padding) -> bool:
        within_x =self.x - padding<= robot_x <= self.x + self.width + padding
        within_y = self.y - padding<= robot_y <= self.y + self.height + padding
        return within_x and within_y
        
