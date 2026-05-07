from pathlib import Path
import re
from enum import Enum
import settings

from appState import AppState

class LawnPointsOption(Enum):
    FIFTY = 0.5
    SEVENTY = 0.7
    NINETY = 0.9
    NINETYFIVE = 0.95
    NINETY_NINE = 0.99
    TESTING = 0.05

def get_milestone_points(total_points: int, option: LawnPointsOption) -> int:
    return round(total_points * option.value)

def data_height_to_points(figure, axis, data_height: float) -> float:
	# Convert a vertical world/data distance to matplotlib points
	pixel0 = axis.transData.transform((0.0, 0.0))[1]
	pixel1 = axis.transData.transform((0.0, data_height))[1]
	return abs(pixel1 - pixel0) * 72.0 / figure.dpi


def sync_linewidth_to_data(path_line, figure, axis, data_height: float) -> None:
	# Set a line's linewidth so it matches a distance in world/data units. 
	path_line.set_linewidth(data_height_to_points(figure, axis, data_height))

def get_milestone_goals(total_points: int, milestones_track: list[LawnPointsOption]) -> list[int]:
    goals = []
    for milestone in milestones_track:
        goals.append(get_milestone_points(total_points, milestone))
    return goals

def log_milestone_result(milestone: float, sub_goal: float, amount_mowed: int, appState: AppState) -> None:
    if amount_mowed>= sub_goal and milestone not in appState.done_milestones:
        velocity = settings.ROBOT_REAL_SPEED_MPS
        energy = (settings.ROBOT_POWER/velocity) * appState.distance if velocity > 0 else 0 
        data = {"percentage_done":f"{int(milestone * 100)}%", "total length": round(appState.distance,2), "total collision": appState.collisions, "total energy": round(energy,2),"total_time":round(appState.time,2)}
        
        appState.addResult(data)
        appState.addDoneMileStone(milestone)

def save_simulation_results(appState: AppState) -> Path:
    project_root = Path(__file__).resolve().parent
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    obstacle_status = "yes" if appState.has_obstacles else "no"
    file_prefix = f"result-{appState.simulation_option}-{obstacle_status}."
    increment_pattern = re.compile(rf"{re.escape(file_prefix)}(\d+)\.txt$")

    highest_increment = 0
    for existing_file in results_dir.glob(f"{file_prefix}*.txt"):
        match = increment_pattern.match(existing_file.name)
        if match:
            highest_increment = max(highest_increment, int(match.group(1)))

    next_increment = highest_increment + 1
    result_path = results_dir / f"{file_prefix}{next_increment}.txt"
    simulation_mode = "animated" if appState.animate_simulation else "instant"

    lines = [
        f"Robot name: {appState.robot_name}",
        f"Simulation option: {appState.simulation_option}",
        f"Simulation mode: {simulation_mode}",
        f"Obstacles: {obstacle_status}",
        f"Total time: {round(appState.time, 2)}",
        f"Total distance: {round(appState.distance, 2)}",
        f"Total collisions: {appState.collisions}",
        "",
        "Results:",
    ]

    if appState.results:
        for index, result in enumerate(appState.results, start=1):
            lines.append(f"{index}. {result}")
    else:
        lines.append("No milestone results were recorded.")

    result_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result_path