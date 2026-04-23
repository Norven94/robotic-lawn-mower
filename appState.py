from dataclasses import dataclass, field

@dataclass
class AppState:
    is_running: bool = False
    time: float = 0.0
    distance: float = 0.0
    collisions: int = 0
    results: list = field(default_factory=list)
    done_milestones: set = field(default_factory=set)
    is_colliding: bool = False
    simulation_option: str = ""
    animate_simulation: bool = True
    robot_name: str = ""
    time: float = 0.0
    has_obstacles: bool = False
    is_running: bool = True

    def addResult(self, data: dict[str, str | int | float]) -> None:
        self.results.append(data)
    
    def addDoneMileStone(self, milestone: float) -> None:
        if milestone not in self.done_milestones:
            self.done_milestones.add(milestone)
    
