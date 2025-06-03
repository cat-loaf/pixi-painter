from enum import Enum

# region Types
type RGBA = tuple[int, int, int, int]
type RGB = tuple[int, int, int]
type HSV = tuple[int, int, int]
# endregion

# region Constants
HUE_MAX = 360
SATURATION_MAX = 100
VALUE_MAX = 100
COLOR_PICKER_TOLERANCE = 3
HUE_PICKER_TOLERANCE = 3
# endregion


# region Enums
class BrushTypes(Enum):
    """
    Enum for different brush types.
    """

    DEFAULT = "default"
    SQUARE = "square"
    CIRCLE = "circle"


# endregion
