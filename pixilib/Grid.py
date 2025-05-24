from typing import Any
from .Cell import Cell
from .Helpers import RGBA, stack_rgba


class Grid:
    """Grid class for managing a grid of cells with RGBA values"""

    def __init__(self, width: int, height: int, default_value: RGBA = (0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.cells = [
            [Cell(x, y, default_value) for x in range(width)] for y in range(height)
        ]

    def __getitem__(self, index: tuple[int, int]):
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        else:
            raise IndexError("Index out of bounds")

    def __setitem__(self, index: tuple[int, int], value: RGBA):
        x, y = index
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x].set_color(value)
        else:
            raise IndexError("Index out of bounds")


class ComputedLayeredGrid:
    """Layered grid class that computes RGB from stacked RGBA layers of grids"""

    def __init__(self, width: int, height: int):
        # All layers must match width and height
        self.width = width
        self.height = height

        # All layers
        self.layers: list[Grid] = []

        # Computed Grid (combine RGBA values into RGB since rendering doesn't support RGBA)
        self._computed_grid: Grid = Grid(width, height)

    def add_layer(self, grid: Grid, insert: int = -1):
        """Add a grid to the layers at index `insert`

        Args:
            grid (Grid): The grid to add
            insert (int, optional): _description_. Defaults to -1

        Raises:
            ValueError: Grid (to add) dimensions should match `self.width` and `self.height`
        """
        if grid.width != self.width or grid.height != self.height:
            raise ValueError("Grid dimensions do not match")

        if insert < 0:
            insert = len(self.layers)

        self.layers.insert(insert, grid)

        self._update_computed_grid()

    def _update_computed_grid(self):
        """Internal method, Updates computed grid only if calculated values differ from stored values"""
        for y in range(self.height):
            for x in range(self.width):
                # Update only if computed grid is different from actual computed grid
                if self._computed_grid[x, y].value != self._compute_cell(x, y):
                    self._computed_grid[x, y].value = self._compute_cell(x, y)

    def _compute_cell(self, x: int, y: int) -> RGBA:
        """Internal method, Stack all RGBA values from all layers at `(x,y)` and return computed RGBA value

        Args:
            x (int): X coordinate of cells to calculate
            y (int): Y coordinate of cells to calculate

        Returns:
            RGBA: stacked RGBA value of all layers at `(x,y)`
        """
        cells: list[RGBA] = []
        i: int = len(self.layers) - 1  # Reverse order (start from highest layer)
        while i >= 0:
            cell = self.layers[i][x, y]
            if cell.value[3] > 0:  # If not transparent, include in calculation
                cells.append(cell.value)
            i -= 1

        # If no colors, return transparent black
        if len(cells) == 0:
            return (0, 0, 0, 0)

        # Calculate stacked color
        i = 0
        while len(cells) > 1:
            c1 = cells[i]
            c2 = cells[i + 1]
            new_color = stack_rgba(c1, c2)
            cells.pop(i)
            cells.pop(i)
            cells.insert(i, new_color)

        return cells[0]

    def get_computed_grid(self) -> Grid:
        """Returns computed grid"""
        return self._computed_grid

    def get_computed_grid_cells(self) -> list[list[Cell]]:
        """Returns the cells in list[list[Cell]] format"""
        return self._computed_grid.cells

    def __getitem__(self, index: tuple[int, int, int]):
        if len(index) != 3:
            x, y = index
            layer = 0
        else:
            x, y, layer = index

        if (
            0 <= x < self.width
            and 0 <= y < self.height
            and 0 <= layer < len(self.layers)
        ):
            return self.layers[layer][x, y]
        else:
            raise IndexError("Index out of bounds")

    def __setitem__(self, index: tuple[int, int, int], value: RGBA):
        if len(index) != 3:
            x, y = index
            layer = 0
        else:
            x, y, layer = index
        if (
            0 <= x < self.width
            and 0 <= y < self.height
            and 0 <= layer < len(self.layers)
        ):
            self.layers[layer][x, y] = value
            self._update_computed_grid()
        else:
            raise IndexError("Index out of bounds")
