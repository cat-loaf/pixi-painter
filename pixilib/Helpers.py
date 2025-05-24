import numpy as np

type RGBA = tuple[int, int, int, int]
type RGB = tuple[int, int, int]


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min(value, max_value), min_value)


def stack_rgba(c1: RGBA, c2: RGBA) -> RGBA:
    alpha = 255 - ((255 - c1[3]) * (255 - c2[3]) / 255)
    if alpha == 0:
        return (0, 0, 0, 0)
    r = (c1[0] * c1[3] + c2[0] * c2[3] * (255 - c1[3]) / 255) / alpha
    g = (c1[1] * c1[3] + c2[1] * c2[3] * (255 - c1[3]) / 255) / alpha
    b = (c1[2] * c1[3] + c2[2] * c2[3] * (255 - c1[3]) / 255) / alpha
    return (int(r), int(g), int(b), int(alpha))


def rgba_to_rgb(rgba: RGBA, background: RGB = (255, 255, 255)) -> RGB:
    return stack_rgba(rgba, (background[0], background[1], background[2], 255))[:3]


def rgb_to_packedint(rgb: RGB) -> int:
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
