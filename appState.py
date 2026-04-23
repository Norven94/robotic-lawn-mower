from dataclasses import dataclass

@dataclass
class AppState:
    is_running: bool = False
    time: float = 0.0
    distance: float = 0.0
    collisions: int = 0
    results: list = []
    logged_milestones: set = set()
    is_colliding: bool = False
    simulation_option: str = ""
    robot_name: str = ""
    time: float = 0.0
    has_obstacles: bool = False
    is_running: bool = True
    
