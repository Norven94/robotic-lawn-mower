from enum import Enum
import settings

class LawnPointsOption(Enum):
    FIFTY = 0.5
    SEVENTY = 0.7
    NINETY = 0.9
    NINETYFIVE = 0.95
    TESTING = 0.01

def getLawnPoints(max_x, min_x, max_y, min_y, option: LawnPointsOption) -> float:
    width_tot = max_x - min_x
    height_tot = max_y - min_y

    #Hämta procentvärde från enum baserat på det valda alternativet
    ratio = option.value

    #Räkna ut hur många punkter det finns på en viss procent (ratio) av ytan
    total_points = (width_tot * height_tot) / (settings.MOVE_DISTANCE ** 2)
    return total_points * ratio

