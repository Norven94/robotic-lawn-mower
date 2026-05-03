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

    #List for obstacles, circular and rectangular.
    def __post_init__ (self):
        house = RectangleObstacles( settings.OFF_SET_PLOT_X, settings.OFF_SET_PLOT_Y, settings.HOUSE_SIZE, settings.HOUSE_SIZE )
        playhouse = RectangleObstacles( 5, 15, 3, 2 )
        garage = RectangleObstacles( 12, 0, 4, 2 )
        pool = CircleObstacles(25, 25, 2.5)
        self.all_obstacles.append(house)
        self.all_obstacles.append(playhouse)
        self.all_obstacles.append(garage)
        self.all_obstacles.append(pool)

    # Helper function to setup all obstacle elements for the world to render
    def getPatches(self) -> list[Rectangle | Circle]:
        patches: list[Rectangle | Circle] = []

        #Rectangle
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
            
            #Cirle
            if obstacle.type == "circle":
                # Add code here to handle rendering of circular elements.
                renderd_obstacle = Circle(
                    (obstacle.x, obstacle.y),
                    obstacle.radius,
                    fill=True,
                    facecolor=settings.HOUSE_COLOR,
                    edgecolor="black",
                    linewidth=2,
                    zorder=2,
                )
                obstacle_border = Circle(
                    (obstacle.x, obstacle.y),
                    obstacle.radius + settings.ROBOT_SIZE,
                    fill=False,
                    edgecolor=settings.BOUNDARY_COLOR,
                    linewidth=2,
                    linestyle="--",
                    zorder=2,
                )
                patches.append(renderd_obstacle)
                patches.append(obstacle_border)

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

#This is a class to represent circular obstacles, which can be used to represent for example a pool.     
@dataclass
class CircleObstacles:
    x: float
    y: float
    radius: float
    width: float = field(init=False)
    height: float = field(init=False)
    type: str = "circle"
    
    def __post_init__(self):
        self.width = self.radius * 2
        self.height = self.radius * 2

    def is_hitting(self, robot_x, robot_y, padding) -> bool:
        distance = ((robot_x - self.x)**2 + (robot_y - self.y)**2)**0.5
        return distance <= (self.raduis + padding)