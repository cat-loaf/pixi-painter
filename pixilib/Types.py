from enum import Enum

type RGBA = tuple[int, int, int, int]
type RGB = tuple[int, int, int]


class BrushTypes(Enum):
    """
    Enum for different brush types.
    """

    DEFAULT = "default"
    SQUARE = "square"
    CIRCLE = "circle"
