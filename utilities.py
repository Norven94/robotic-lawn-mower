from enum import Enum
import settings
import appState

class LawnPointsOption(Enum):
    FIFTY = 0.5
    SEVENTY = 0.7
    NINETY = 0.9
    NINETYFIVE = 0.95
    TESTING = 0.05

def getLawnPoints(max_x, min_x, max_y, min_y, option: LawnPointsOption) -> float:
    width_tot = max_x - min_x
    height_tot = max_y - min_y

    #Hämta procentvärde från enum baserat på det valda alternativet
    ratio = option.value

    #Räkna ut hur många punkter det finns på en viss procent (ratio) av ytan
    total_points = (width_tot * height_tot) / (settings.MOVE_DISTANCE ** 2)
    return total_points * ratio

def data_height_to_points(figure, axis, data_height: float) -> float:
	# Convert a vertical world/data distance to matplotlib points
	pixel0 = axis.transData.transform((0.0, 0.0))[1]
	pixel1 = axis.transData.transform((0.0, data_height))[1]
	return abs(pixel1 - pixel0) * 72.0 / figure.dpi


def sync_linewidth_to_data(path_line, figure, axis, data_height: float) -> None:
	# Set a line's linewidth so it matches a distance in world/data units. 
	path_line.set_linewidth(data_height_to_points(figure, axis, data_height))

def get_milestone_goals(lawn, milestones_track: list[LawnPointsOption]) -> list[float]:
    goals = []
    for m in milestones_track:
          points = getLawnPoints(lawn.max_x,lawn.min_x,lawn.max_y,lawn.min_y,m)
          goals.append(points)
    return goals

def log_milestone_result(m, energy:float):
    data = {"percentage_done":f"{int(m.value * 100)}%", "total length": round(appState.distance,2), "total collision": appState.collisions, "total energy": round(energy,2),"total_time":round(appState.time,2)}
    appState.results.append(data)
    appState.logged_milestones.add(m)