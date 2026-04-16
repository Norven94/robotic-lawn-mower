LAWN_MIN_X = 0.0
LAWN_MAX_X = 30.0
LAWN_MIN_Y = 0.0
LAWN_MAX_Y = 30.0

# Simulation settings
# If we change this to 1000ms we get 1 step per second which is better to use for correct statistics,
# but for development we want it to be faster so we can see the results quicker. We need to rethink this 
# when we implement statistics capturing.
ANIMATION_INTERVAL_MS = 80 
# Only effects the window size displayed on the screen, not 
# the actual lawn dimensions
FIGURE_SIZE = (10, 10)

# Robot settings
ROBOT_START_X = 5.0
ROBOT_START_Y = 5.0
ROBOT_DIAMETER = 0.25
ROBOT_BODY_OFFSET = 0.1
ROBOT_SIZE = ROBOT_DIAMETER + ROBOT_BODY_OFFSET
ROBOT_START_HEADING = 0.0
MOVE_DISTANCE = ROBOT_DIAMETER
ROBOT_REAL_SPEED_MPS = 0.42

#Obstacle settings
HOUSE_SIZE = 10.0
OFF_SET_PLOT_X = 10.0
OFF_SET_PLOT_Y = 10.0
HOUSE_COLOR = "#000000"

# CLI settings
DEFAULT_ROBOT_NAME = "Per"

# Colors
LAWN_COLOR = "#d8f3c0"
MOWED_COLOR = "#7fb069"
PATH_COLOR = "#386641"
ROBOT_COLOR = "#bc4749"
BOUNDARY_COLOR = "#2d6a4f"

