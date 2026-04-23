from collections.abc import Callable, Iterator


class GridCoverage:
    # Maps world coordinates onto a fixed mowing grid so both controllers
    # are measured against the same coverage model.
    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float, step: float) -> None:
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.step = step

    def cell_key(self, x: float, y: float) -> tuple[int, int]:
        return (
            round((x - self.min_x) / self.step),
            round((y - self.min_y) / self.step),
        )

    def cell_center(self, cell_key: tuple[int, int]) -> tuple[float, float]:
        return (
            self.min_x + cell_key[0] * self.step,
            self.min_y + cell_key[1] * self.step,
        )

    def iter_cell_keys(self) -> Iterator[tuple[int, int]]:
        x_steps = round((self.max_x - self.min_x) / self.step)
        y_steps = round((self.max_y - self.min_y) / self.step)
        for x_index in range(x_steps + 1):
            for y_index in range(y_steps + 1):
                yield (x_index, y_index)

    def collect_valid_cells(
        self,
        is_valid_cell: Callable[[float, float], bool],
    ) -> set[tuple[int, int]]:
        # Precompute every reachable cell once so milestone targets can use
        # mowable area instead of the full rectangular lawn area.
        valid_cells: set[tuple[int, int]] = set()
        for cell_key in self.iter_cell_keys():
            cell_x, cell_y = self.cell_center(cell_key)
            if is_valid_cell(cell_x, cell_y):
                valid_cells.add(cell_key)
        return valid_cells

    def nearest_valid_cell_key(
        self,
        valid_cells: set[tuple[int, int]],
        x: float,
        y: float,
    ) -> tuple[int, int] | None:
        # Map an actual robot position back onto the nearest reachable grid
        # cell so free-angle wired movement and grid-based GPS runs are counted
        # consistently.
        cell_key = self.cell_key(x, y)
        if cell_key in valid_cells:
            return cell_key

        nearest_key: tuple[int, int] | None = None
        nearest_distance: float | None = None
        for x_offset in (-1, 0, 1):
            for y_offset in (-1, 0, 1):
                candidate_key = (cell_key[0] + x_offset, cell_key[1] + y_offset)
                if candidate_key not in valid_cells:
                    continue
                candidate_x, candidate_y = self.cell_center(candidate_key)
                distance = (candidate_x - x) ** 2 + (candidate_y - y) ** 2
                if nearest_distance is None or distance < nearest_distance:
                    nearest_key = candidate_key
                    nearest_distance = distance

        return nearest_key