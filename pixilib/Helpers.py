from numbers import Number
import numpy as np
from .Types import RGB, RGBA


def clamp(value: Number, min_value: Number, max_value: Number) -> Number:
    """Clamp a value between a minimum and maximum value

    Args:
        value (Number): The value to clamp
        min_value (Number): The minimum value
        max_value (Number): The maximum value

    Returns:
        Number: The clamped value, which will be between min_value and max_value
    """
    return max(min(value, max_value), min_value)


def overflow(value: Number, min_value: Number, max_value: Number) -> Number:
    """Overflow a value between a minimum and maximum value

    Args:
        value (Number): The value to overflow
        min_value (Number): The minimum value
        max_value (Number): The maximum value

    Returns:
        Number: The overflowed value, which will be between min_value and max_value
    """
    return (value - min_value) % (max_value - min_value) + min_value


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
