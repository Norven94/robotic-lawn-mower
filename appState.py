from dataclasses import dataclass

from controller import RandomController, WireController

@dataclass
class AppState:
    simulation_option: str | None = None
    is_running: bool = False
time=0