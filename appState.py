from dataclasses import dataclass

@dataclass
class AppState:
    simulation_option: str | None = None
    is_running: bool = False
time=0
distance = 0
collisions = 0

results = []
logged_milestones = set()

is_colliding = False