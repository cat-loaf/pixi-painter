from abc import ABC, abstractmethod
from .Grid import Grid
from .Types import RGBA, BrushTypes
from .Color import ColorSelector
from .Helpers import flood_fill, line, chunks, rgba_to_hsva
from collections import deque
from concurrent.futures import ThreadPoolExecutor


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
        return "paintbrush"

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
            return

        if radius == 0:
            if data["x"] is None or data["y"] is None:
                data["x"] = x
                data["y"] = y
            return LineTool.mouse_up(grid, x, y, color, data, layer)

        coords_to_paint = []

        match radius_type:
            case BrushTypes.SQUARE:
                if radius == 1:
                    if 0 <= x < grid.width and 0 <= y < grid.height:
                        coords_to_paint.append((x, y))
                    if 0 <= x - 1 < grid.width and 0 <= y < grid.height:
                        coords_to_paint.append((x - 1, y))
                    if 0 <= x < grid.width and 0 <= y - 1 < grid.height:
                        coords_to_paint.append((x, y - 1))
                    if 0 <= x - 1 < grid.width and 0 <= y - 1 < grid.height:
                        coords_to_paint.append((x - 1, y - 1))

                radius -= 1

                for i in range(-radius, radius + 1):
                    for j in range(-radius, radius + 1):
                        xi, yj = x + i, y + j
                        if 0 <= xi < grid.width and 0 <= yj < grid.height:
                            coords_to_paint.append((xi, yj))

            case BrushTypes.CIRCLE | _:
                for i in range(-radius, radius + 1):
                    for j in range(-radius, radius + 1):
                        if i * i + j * j <= radius * radius:
                            xi, yj = x + i, y + j
                            if 0 <= xi < grid.width and 0 <= yj < grid.height:
                                coords_to_paint.append((xi, yj))

        batch_size = 256 if radius >= 4 else 64

        def paint_batch(batch):
            for pos in batch:
                grid[*pos] = color

        with ThreadPoolExecutor() as executor:
            executor.map(paint_batch, chunks(coords_to_paint, batch_size))


class EraserTool(Tool):
    """Tool for erasing"""

    def __str__():
        return "eraser"

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
        return "fill"

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
        return "line"

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
        radius: int = 0,
        *args,
        **kwargs,
    ):
        if isinstance(grid, Grid):
            line(
                x1=x,
                y1=y,
                x2=x2,
                y2=y2,
                grid=grid,
                color=color,
                layer=layer,
                radius=radius,
                grid_type="Grid",
            )
        else:
            line(
                x1=x,
                y1=y,
                x2=x2,
                y2=y2,
                grid=grid,
                color=color,
                layer=layer,
                radius=radius,
            )

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


class ClearTool(Tool):
    """Tool for clearing the grid"""

    def __str__():
        return "clear"

    def run(grid: Grid, color: RGBA, *args, **kwargs):
        """Clears the grid by filling it with the specified color.

        Args:
            grid (Grid): The grid to clear.
            color (RGBA): The color to fill the grid with.
        """
        grid.clear(color)


class PanTool(Tool):
    """Tool for panning the view"""

    def __str__():
        return "pan"

    def run(*args, **kwargs):
        """Panning does not require any specific action."""
        pass


class EyedropperTool(Tool):
    def __str__():
        return "eyedropper"

    def run(
        grid: Grid,
        x: int,
        y: int,
        color_selector: ColorSelector,
        layer: int = None,
        *args,
        **kwargs,
    ):
        """Picks the color at the specified coordinates.

        Args:
            grid (Grid): The grid to pick from.
            x (int): X coordinate to pick from.
            y (int): Y coordinate to pick from.
        """
        cell = (0, 0, 0, 0)
        if 0 <= x < grid.width and 0 <= y < grid.height:
            if layer is not None:
                cell = grid[x, y, layer].value
            else:
                cell = grid[x, y].value

        hsva = rgba_to_hsva(cell)
        color_selector.update_hue(hsva[0])
        color_selector.sat = hsva[1]
        color_selector.val = hsva[2]
        color_selector.color = cell
        color_selector.update_color_display()


mouse_held_tools = [PaintTool, EraserTool]
mouse_up_tools = [LineTool]
mouse_pressed_tools = [FillTool, ClearTool, EyedropperTool]


mouse_preview_tools = [PaintTool, LineTool, FillTool, ClearTool]
no_cursor_grid_preview = [LineTool]

toolset: list[Tool] = [
    PaintTool,
    EraserTool,
    LineTool,
    FillTool,
    ClearTool,
    PanTool,
    EyedropperTool,
]

toolset_indexes = [a.__str__() for a in toolset]
