from abc import ABC, abstractmethod
from .Grid import Grid
from .Types import RGBA, BrushTypes
from .Helpers import color_diff
from collections import deque


class Tool(ABC):
    """
    Abstract base class for tools.
    """

    @abstractmethod
    def __str__():
        pass

    @abstractmethod
    def run(*args, **kwargs):
        """
        Run the tool with the given arguments.
        """
        pass


class PaintTool(Tool):
    """Tool for painting"""

    def __str__():
        return "Paint Tool"

    def run(
        grid: Grid,
        x: int,
        y: int,
        color: RGBA,
        layer: int = 0,
        radius: int = 0,
        radius_type: BrushTypes = BrushTypes.CIRCLE,
        *args,
        **kwargs,
    ):
        """Paints on the grid at the specified coordinates with the given color.

        Args:
            grid (Grid): Grid to paint on
            x (int): X origin or X coordinate
            y (int): Y origin or Y coordinate
            color (RGBA): Color to paint
            layer (int, optional): Layer to paint on. Defaults to 0.
            radius (int, optional): Radius of brush. Defaults to 0.
            radiusType (BrushTypes, optional): Brush Type. Defaults to BrushTypes.CIRCLE.

        Raises:
            ValueError: Coordinates are out of bounds of the grid.
        """

        if x < 0 or x >= grid.width or y < 0 or y >= grid.height:
            raise ValueError("Coordinates are out of bounds of the grid.")

        if radius == 0:
            grid[x, y] = color
            return

        match radius_type:
            case BrushTypes.SQUARE:
                if radius == 1:
                    if 0 <= x < grid.width and 0 <= y < grid.height:
                        grid[x, y, layer] = color
                    if 0 <= x + 1 < grid.width and 0 <= y < grid.height:
                        grid[x + 1, y, layer] = color
                    if 0 <= x < grid.width and 0 <= y + 1 < grid.height:
                        grid[x, y + 1, layer] = color
                    if 0 <= x + 1 < grid.width and 0 <= y + 1 < grid.height:
                        grid[x + 1, y + 1, layer] = color
                    return

                radius -= 1

                for i in range(-radius, radius + 1):
                    for j in range(-radius, radius + 1):
                        if (
                            x + i < 0
                            or x + i >= grid.width
                            or y + j < 0
                            or y + j >= grid.height
                        ):
                            continue
                        grid[x + i, y + j, layer] = color

            case BrushTypes.CIRCLE | _:
                for i in range(-radius, radius + 1):
                    for j in range(-radius, radius + 1):
                        if i * i + j * j <= radius * radius:
                            if (
                                x + i < 0
                                or x + i >= grid.width
                                or y + j < 0
                                or y + j >= grid.height
                            ):
                                continue
                            grid[x + i, y + j, layer] = color


class EraserTool(Tool):
    """Tool for erasing"""

    def __str__():
        return "Eraser Tool"

    def run(
        grid: Grid,
        x: int,
        y: int,
        layer: int = 0,
        radius: int = 0,
        radiusType: BrushTypes = BrushTypes.CIRCLE,
        *args,
        **kwargs,
    ):
        """Paints on the grid at the specified coordinates with the given color.

        Args:
            grid (Grid): Grid to paint on
            x (int): X origin or X coordinate
            y (int): Y origin or Y coordinate
            layer (int, optional): Layer to paint on. Defaults to 0.
            radius (int, optional): Radius of brush. Defaults to 0.
            radiusType (BrushTypes, optional): Brush Type. Defaults to BrushTypes.CIRCLE.

        Raises:
            ValueError: Coordinates are out of bounds of the grid.
        """

        color = (0, 0, 0, 0)  # Transparent color for erasing
        return PaintTool.run(grid, x, y, color, layer, radius, radiusType)


class FillTool(Tool):
    """Tool for filling an area with a color"""

    def __str__():
        return "Fill Tool"

    def run(
        grid: Grid,
        x: int,
        y: int,
        color: RGBA,
        layer: int = 0,
        tolerance: int = 0,
        *args,
        **kwargs,
    ):
        if x < 0 or x >= grid.width or y < 0 or y >= grid.height:
            raise ValueError("Coordinates are out of bounds of the grid.")

        rows, cols = grid.width, grid.height

        repl_color = grid[x, y, layer].value

        if color_diff(repl_color, color) == 0:
            return

        visited = [[False] * cols for _ in range(rows)]
        queue = deque([(x, y)])

        while queue:
            cx, cy = queue.popleft()

            if not (0 <= cx < cols and 0 <= cy < rows):
                continue
            if visited[cx][cy]:
                continue

            cur_color = grid[cx, cy].value

            if color_diff(cur_color, repl_color) <= tolerance:
                grid[cx, cy, layer] = color
                visited[cx][cy] = True

                queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])


mouse_held_tools = [PaintTool, EraserTool]
mouse_pressed_tools = [FillTool]
