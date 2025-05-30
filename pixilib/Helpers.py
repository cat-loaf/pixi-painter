from numbers import Number
from typing import Iterable
import numpy as np
from .Types import RGB, RGBA
from collections import deque


def clamp(value: Number, min_value: Number, max_value: Number) -> Number:
    """Clamp a value between a minimum and maximum value. End-inclusive

    Args:
        value (Number): The value to clamp
        min_value (Number | None): The minimum value, if None, no lower bound
        max_value (Number | None): The maximum value, if None, no upper bound

    Returns:
        Number: The clamped value, which will be between min_value and max_value
    """
    if min_value is None and max_value is None:
        return value
    if min_value is None:
        return min(value, max_value)
    if max_value is None:
        return max(value, min_value)
    return max(min_value, min(value, max_value))


def overflow(value: Number, min_value: Number, max_value: Number) -> Number:
    """Overflow a value between a minimum and maximum value. End-inclusive

    Args:
        value (Number): The value to overflow
        min_value (Number | None): The minimum value, if None, no lower bound
        max_value (Number | None): The maximum value, if None, no upper bound

    Returns:
        Number: The overflowed value, which will be between min_value and max_value
    """
    if min_value is None and max_value is None:
        return value
    if min_value is None:
        return value % max_value
    if max_value is None:
        return value % min_value
    range_size = max_value - min_value + 1
    return (value - min_value) % range_size + min_value


def stack_rgba(c1: RGBA, c2: RGBA) -> RGBA:
    """Stack two RGBA colors together, taking into account their alpha values

    Args:
        c1 (RGBA): First color
        c2 (RGBA): Second color

    Returns:
        RGBA: Stacked RGBA color resulting from blending c1 and c2
    """
    a1, a2 = c1[3] / 255.0, c2[3] / 255.0
    out_a = a1 + a2 * (1 - a1)

    if out_a == 0:
        return (0, 0, 0, 0)

    r = (c1[0] * a1 + c2[0] * a2 * (1 - a1)) / out_a
    g = (c1[1] * a1 + c2[1] * a2 * (1 - a1)) / out_a
    b = (c1[2] * a1 + c2[2] * a2 * (1 - a1)) / out_a

    return (int(r + 0.5), int(g + 0.5), int(b + 0.5), int(out_a * 255 + 0.5))


def rgba_to_rgb(rgba: RGBA, background: RGB = (255, 255, 255)) -> RGB:
    """Convert an RGBA color to RGB, using a background color for transparency

    Args:
        rgba (RGBA): The RGBA color to convert
        background (RGB, optional): Background to use for stacking Defaults to (255, 255, 255)

    Returns:
        RGB: The RGB color resulting from the conversion
    """
    r, g, b, a = rgba
    alpha = a / 255.0
    inv_alpha = 1 - alpha

    r_out = int(r * alpha + background[0] * inv_alpha + 0.5)
    g_out = int(g * alpha + background[1] * inv_alpha + 0.5)
    b_out = int(b * alpha + background[2] * inv_alpha + 0.5)

    return (r_out, g_out, b_out)


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
    target_color: RGBA,
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
    cols, rows = grid.width, grid.height

    if not in_grid(x, y, cols, rows):
        raise ValueError(
            f"Coordinates are out of bounds of the grid. {x=} {y=} {cols=} {rows=}"
        )

    target_color = grid[x, y, layer].value

    if color_diff(target_color, color) == 0:
        return

    visited = [[False for _ in range(cols)] for _ in range(rows)]
    queue = deque([(x, y)])

    while queue:
        cx, cy = queue.popleft()

        if not (0 <= cx < cols and 0 <= cy < rows):
            continue
        if visited[cy][cx]:
            continue

        cur_color = grid[cx, cy].value

        if color_diff(cur_color, target_color) <= tolerance:
            grid[cx, cy, layer] = color
            visited[cy][cx] = True

            queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])


def chunks(l: list, batch_size: int) -> Iterable[list]:
    """Yield successive n-sized chunks from l.

    Args:
        l (list): List to chunk
        batch_size (int): Size of each chunk

    Yields:
        list: Chunks of the original list
    """
    for i in range(0, len(l), batch_size):
        yield l[i : i + batch_size]
