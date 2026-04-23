from dataclasses import dataclass

@dataclass
class AppState:
    simulation_option: str = ""
    robot_name: str = ""
    time: float = 0.0
    has_obstacles: bool = False
    is_running: bool = True
    