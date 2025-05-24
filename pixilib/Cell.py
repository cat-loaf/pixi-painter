from typing import Any
from .Types import RGBA


class Cell:
    def __init__(self, x: int, y: int, default_value: RGBA = (0, 0, 0, 0)):
        self.x = x
        self.y = y
        self.value = default_value

    def __repr__(self):
        return f"Cell({self.x}, {self.y}, {self.value})"

    def set_color(self, color: RGBA) -> RGBA:
        """Set value of cell to new RGBA color, and return old value

        Args:
            color (RGBA): New RGBA color to set

        Raises:
            ValueError: RGBA(x,x,x,x) values must be between 0 and 255

        Returns:
            RGBA: Old RGBA color value of the cell
        """
        if any(map(lambda c: c < 0 or c > 255, color)):
            raise ValueError("Color values must be between 0 and 255")
        self.value = color
