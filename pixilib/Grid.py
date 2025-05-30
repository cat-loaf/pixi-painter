from typing import Any
from .Cell import Cell
from .Helpers import stack_rgba
from .Types import RGBA


class Grid:
    """Grid class for managing a grid of cells with RGBA values"""

    def __init__(self, width: int, height: int, default_value: RGBA = (0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.cells = [
            [Cell(x, y, default_value) for x in range(width)] for y in range(height)
        ]

    def __getitem__(self, index: tuple[int, int]):
        if len(index) > 2:
            x, y, _ = index
        else:
            x, y = index

        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None

    def __setitem__(self, index: tuple[int, int], value: RGBA):
        if len(index) > 2:
            x, y, _ = index
        else:
            x, y = index

        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x].set_color(value)
        return None

    def clear(self, value: RGBA = (0, 0, 0, 0)):
        """Clear the grid by setting all cells to the default value"""
        for y in range(self.height):
            for x in range(self.width):
                self.cells[y][x].set_color(value)


class ComputedLayeredGrid:
    """Layered grid class that computes RGB from stacked RGBA layers of grids"""

    def __init__(self, width: int, height: int):
        # All layers must match width and height
        self.width = width
        self.height = height

        self.overlay: Grid = Grid(width, height)

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
        """Internal Method, Updates computed grid only if calculated values differ from stored values"""
        for y in range(self.height):
            for x in range(self.width):
                # Update only if computed grid is different from actual computed grid
                computed_cell = self._compute_cell(x, y)
                if self._computed_grid[x, y].value != computed_cell:
                    self._computed_grid[x, y] = computed_cell

    def _compute_cell(self, x: int, y: int) -> RGBA:
        """Internal Method, Stack all RGBA values from all layers at `(x,y)` and return computed RGBA value

        Args:
            x (int): X coordinate of cells to calculate
            y (int): Y coordinate of cells to calculate

        Returns:
            RGBA: stacked RGBA value of all layers at `(x,y)`
        """
        cells = [
            self.layers[i][x, y].value
            for i in reversed(range(len(self.layers)))
            if self.layers[i][x, y].value[3] > 0
        ]

        if not cells:
            return (0, 0, 0, 0)

        # Blend from bottom to top (reverse of how we collected them)
        result = cells[-1]
        for color in reversed(cells[:-1]):
            result = stack_rgba(color, result)

        return result

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
        return None

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
            computed_cell = self._compute_cell(x, y)
            if self._computed_grid[x, y].value != computed_cell:
                self._computed_grid[x, y] = computed_cell
        return

    def clear(self, value: RGBA = (0, 0, 0, 0), layer: int = -1):
        """Clear the grid or a specific layer by setting all cells to the default value

        Args:
            value (RGBA, optional): The value to set all cells to. Defaults to (0, 0, 0, 0).
            layer (int, optional): The layer to clear. If -1, clears all layers. Defaults to -1.

        Raises:
            IndexError: If the layer index is out of bounds
        """
        if layer == -1:
            # Clear all layers
            for l in self.layers:
                l.clear(value)
        else:
            # Clear specific layer
            if 0 <= layer < len(self.layers):
                self.layers[layer].clear(value)
            else:
                return
        self._update_computed_grid()
