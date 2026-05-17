# Robot Lawn Mower Simulator

This project simulates an autonomous robot lawn mower moving across a rectangular lawn with optional rectangular and circular obstacles. It supports two movement strategies: a random wired controller and a GPS-style serpentine controller that can perform cleanup passes around missed areas and navigate around obstacles.

The simulator can run either as an animated matplotlib visualization or as an instant headless simulation using the same movement logic. During each run it tracks coverage over a mowing grid, travelled distance, elapsed time, collision count, and milestone progress. After the simulation finishes, it writes a text summary to the `results/` folder with the selected controller mode, whether obstacles were enabled, and the recorded run statistics.

The codebase is designed to be easily customizable, making it simple to modify the lawn layout, obstacles, and robot mower configuration. See the `Customizing the simulation` section for more information.

## Project structure

- `index.py` is the application entrypoint. It creates the app state, robot, world, and selected controller, then starts the simulation.
- `cli.py` contains the command-line prompts for simulation mode, obstacle mode, and animation mode.
- `appState.py` stores shared runtime state such as elapsed time, collisions, results, and selected options.
- `controller.py` contains the mower controllers. The project currently includes a random wired controller and a GPS-style serpentine controller with obstacle and cleanup handling.
- `robot.py` defines the `Robot` class and its movement logic.
- `world.py` coordinates the simulation loop, collision checks, rendering, mowing progress, and result logging.
- `lawn.py` defines the lawn boundaries and helper methods used to validate robot movement.
- `obstacles.py` defines the rectangular and circular obstacles and the matplotlib patches used to render them.
- `coverage.py` maps mower movement onto a grid so coverage can be tracked consistently across controllers.
- `utilities.py` contains helper functions for milestone tracking, line-width scaling, and saving result files.
- `settings.py` contains global simulator settings such as lawn size, robot dimensions, movement distance, colors, and animation timing.
- `results/` stores exported text summaries from completed simulation runs.

## Installation requirements

```bash
pip install matplotlib
pip install inquirer
```

## Run

```bash
python index.py
```

## Results

The CLI asks whether the simulation should run as animated or instant. Both modes use the same simulation logic.
After each run, a text file is written to `results/` using this format:

```text
result-{simulation_option}-{yes|no}.{n}.txt
```

In the filename:

- `simulation_option` is the selected controller mode, for example `gps` or `wired`.
- `yes` means obstacles were enabled for that run.
- `no` means obstacles were disabled for that run.

Example:

```text
result-gps-yes.1.txt
```

## Customizing the simulation

### Change lawn size

To change the lawn dimensions, edit the values in `settings.py` (lines 1-4).

### Change or add obstacles

If you want to modify existing obstacles or add new ones, edit the `__post_init__` function in `obstacles.py` around line 33.

Here you can change:
- obstacle size
- obstacle position
- obstacle type
- number of obstacles

### Change robot mower dimensions

If you want to simulate another robot lawn mower with different dimensions, speed, or power consumption, edit the robot settings in `settings.py` (lines 17–25).

### Change/Add robot navigation system 

It's also possible to add new navigation systems on top of the existing ones. New controllers should be added in `controller.py`. You also need to update the available simulation options in `cli.py` to make the new controller selectable from the CLI.

## Simulation examples

### GPS
<img width="1032" height="1071" alt="gps-simulering-2" src="https://github.com/user-attachments/assets/8abf1d90-b1af-4749-aca8-3b3dbdb4cfbd" />

### Wired
<img width="1102" height="1092" alt="slumpad-simulering-2" src="https://github.com/user-attachments/assets/8abc23c4-9d25-4548-87c2-2b3e4407da4b" />

