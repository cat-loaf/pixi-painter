from abc import ABC, abstractmethod
from .Grid import Grid
from .Types import RGBA, BrushTypes
from .Helpers import flood_fill, line
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

    @abstractmethod
    def update(*args, **kwargs):
        """
        Update the tool with the given arguments.
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
        data: dict,
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
            if data["x"] is None or data["y"] is None:
                data["x"] = x
                data["y"] = y
            return LineTool.mouse_up(grid, x, y, color, data, layer)

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
        data: dict,
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
            layer (int, optional): Layer to paint on. Defaults to 0.
            radius (int, optional): Radius of brush. Defaults to 0.
            radiusType (BrushTypes, optional): Brush Type. Defaults to BrushTypes.CIRCLE.

        Raises:
            ValueError: Coordinates are out of bounds of the grid.
        """

        color = (0, 0, 0, 0)  # Transparent color for erasing
        return PaintTool.run(
            grid=grid,
            x=x,
            y=y,
            color=color,
            layer=layer,
            radius=radius,
            radius_type=radius_type,
            data=data,
        )


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
        flood_fill(
            x, y, grid, color, grid[x, y, layer].value, layer=layer, tolerance=tolerance
        )


class LineTool(Tool):
    """Tool for drawing lines"""

    def __str__():
        return "Line Tool"

    def run(
        grid: Grid,
        x: int,
        y: int,
        x2: int,
        y2: int,
        color: RGBA,
        data: dict,
        mouse_held: bool,
        layer: int = 0,
        *args,
        **kwargs,
    ):
        # if mouse_held and data["mouse_held"]:
        #     LineTool.mouse_up(grid, x, y, color, data, layer)

        # data["mouse_held"] = mouse_held
        line(x, y, x2, y2, grid, color, layer)

    def update(x: int, y: int, data: dict, mouse_held: bool, *args, **kwargs):
        data["mouse_held"] = mouse_held
        if mouse_held:
            LineTool.mouse_down(x, y, data)

    def mouse_down(x: int, y: int, data: dict):
        """Store the starting point for the line."""
        data["x"] = x
        data["y"] = y

    def mouse_up(grid: Grid, x: int, y: int, color: RGBA, data: dict, layer: int = 0):
        """Draw the line from the starting point to the current point."""
        line(data["x"], data["y"], x, y, grid, color, layer)
        # Reset the starting point
        data["x"] = None
        data["y"] = None


mouse_held_tools = [PaintTool, EraserTool]
mouse_up_tools = [LineTool]
mouse_pressed_tools = [FillTool]
