from dataclasses import dataclass

@dataclass
class AppState:
    simulation_option: str | None = None
    is_running: bool = False
time=0