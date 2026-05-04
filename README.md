# Robot Lawn Mower Simulator

This project simulates a simple autonomous robot lawn mower using matplotlib animation.

## Project structure

- `settings.py` contains the global simulator settings such as lawn size, robot start position, movement distance, and animation timing.
- `entities.py` contains the `Robot` class and its movement logic.
- `world.py` contains the lawn model and matplotlib rendering loop.
- `index.py` is the application entrypoint.

## Install

```bash
pip install matplotlib
pip install inquirer
```

## Run

```bash
python index.py
```

The CLI now asks whether the simulation should run as animated or instant. Both modes use the same simulation logic.

After each run, a text file is written to `results/` using this format:

```text
result-{simulation_option}-{yes|no}.{n}.txt
```

Example:

```text
result-gps-yes.1.txt
```
