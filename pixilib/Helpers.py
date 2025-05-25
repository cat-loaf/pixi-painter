from numbers import Number
import numpy as np
from .Types import RGB, RGBA
from collections import deque


def clamp(value: Number, min_value: Number, max_value: Number) -> Number:
    """Clamp a value between a minimum and maximum value. End-inclusive

    Args:
        value (Number): The value to clamp
        min_value (Number): The minimum value
        max_value (Number): The maximum value

    Returns:
        Number: The clamped value, which will be between min_value and max_value
    """
    return max(min(value, max_value), min_value)


def overflow(value: Number, min_value: Number, max_value: Number) -> Number:
    """Overflow a value between a minimum and maximum value. End-inclusive

    Args:
        value (Number): The value to overflow
        min_value (Number): The minimum value
        max_value (Number): The maximum value

    Returns:
        Number: The overflowed value, which will be between min_value and max_value
    """
    return max_value if value < min_value else min_value if value > max_value else value


def stack_rgba(c1: RGBA, c2: RGBA) -> RGBA:
    """Stack two RGBA colors together, taking into account their alpha values

    Args:
        c1 (RGBA): First color
        c2 (RGBA): Second color

    Returns:
        RGBA: Stacked RGBA color resulting from blending c1 and c2
    """
    alpha = 255 - ((255 - c1[3]) * (255 - c2[3]) / 255)
    if alpha == 0:
        return (0, 0, 0, 0)
    r = (c1[0] * c1[3] + c2[0] * c2[3] * (255 - c1[3]) / 255) / alpha
    g = (c1[1] * c1[3] + c2[1] * c2[3] * (255 - c1[3]) / 255) / alpha
    b = (c1[2] * c1[3] + c2[2] * c2[3] * (255 - c1[3]) / 255) / alpha
    return (int(r), int(g), int(b), int(alpha))


def rgba_to_rgb(rgba: RGBA, background: RGB = (255, 255, 255)) -> RGB:
    """Convert an RGBA color to RGB, using a background color for transparency

    Args:
        rgba (RGBA): The RGBA color to convert
        background (RGB, optional): Background to use for stacking Defaults to (255, 255, 255)

    Returns:
        RGB: The RGB color resulting from the conversion
    """
    return stack_rgba(rgba, (background[0], background[1], background[2], 255))[:3]


def rgb_to_packedint(rgb: RGB) -> int:
    """Convert an RGB color to a packed integer (to be used for pixels2d)

    Args:
        rgb (RGB): Color to convert

    Returns:
        int: Packed integer representation of the RGB color
    """
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]


def rgb_to_hex(rgb: RGB | RGBA) -> str:
    """Convert an RGB color to a hexadecimal string

    Args:
        rgb (RGB): Color to convert

    Returns:
        str: Hexadecimal string representation of the RGB color
    """
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def color_diff(c1: RGBA, c2: RGBA) -> float:
    """Euclidean distance between two RGBA colors
    Args:
        c1 (RGBA): First color
        c2 (RGBA): Second color
    """
    return np.sqrt(
        (c1[0] - c2[0]) ** 2
        + (c1[1] - c2[1]) ** 2
        + (c1[2] - c2[2]) ** 2
        + (c1[3] - c2[3]) ** 2
    )


def in_grid(x: int, y: int, width: int, height: int) -> bool:
    """Check if coordinates are within the bounds of a grid

    Args:
        x (int): X coordinate
        y (int): Y coordinate
        width (int): Width of the grid
        height (int): Height of the grid

    Returns:
        bool: True if coordinates are within bounds, False otherwise
    """
    return 0 <= x < width and 0 <= y < height


def on_screen(x: int, y: int, screen_width: int, screen_height: int) -> bool:
    """Check if coordinates are within the bounds of a screen

    Args:
        x (int): X coordinate
        y (int): Y coordinate
        screen_width (int): Width of the screen
        screen_height (int): Height of the screen

    Returns:
        bool: True if coordinates are within bounds, False otherwise
    """
    return 0 <= x < screen_width and 0 <= y < screen_height


def line(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    grid: "Grid",  # type: ignore
    color: RGBA,
    layer: int = 0,
    grid_type: str = "ComputedLayeredGrid",
    radius: int = 0,
):
    """Draw a line on the grid from (x1, y1) to (x2, y2) using Bresenham's line algorithm

    Args:
        x1 (int): Starting X coordinate
        y1 (int): Starting Y coordinate
        x2 (int): Ending X coordinate
        y2 (int): Ending Y coordinate
        grid (ComputedLayeredGrid): Grid to draw the line on
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        if not in_grid(x1, y1, grid.width, grid.height):
            break

        if grid_type == "ComputedLayeredGrid":
            location = (x1, y1, layer)
        else:
            location = (x1, y1)

        grid[location] = color
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                if in_grid(x1 + i, y1 + j, grid.width, grid.height):
                    grid[x1 + i, y1 + j] = color

        if x1 == x2 and y1 == y2:
            break
        err2 = err * 2

        if err2 > -dy:
            err -= dy
            x1 += sx

        if err2 < dx:
            err += dx
            y1 += sy


def flood_fill(
    x: int,
    y: int,
    grid: "ComputedLayeredGrid",
    color: RGBA,
    repl_color: RGBA,
    layer: int = 0,
    tolerance: float = 0.0,
):
    """Flood fill algorithm to fill an area with a color

    Args:
        x (int): X coordinate to start filling from
        y (int): Y coordinate to start filling from
        grid (ComputedLayeredGrid): Grid to fill
        color (RGBA): Color to replace
        repl_color (RGBA): Color to fill with
        layer (int, optional): Layer to fill on. Defaults to 0.
    """
    if not in_grid(x, y, grid.width, grid.height):
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
