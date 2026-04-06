from dataclasses import dataclass

from controller import RandomController, WireController

@dataclass
class AppState:
    simulation_option: RandomController | WireController | None = None
    is_running: bool = False