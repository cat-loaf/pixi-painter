from .Types import (
    RGBA,
    RGB,
    HSV,
    HUE_MAX,
    SATURATION_MAX,
    VALUE_MAX,
    COLOR_PICKER_TOLERANCE,
    HUE_PICKER_TOLERANCE,
)
from .Helpers import hsva_to_rgba, rgb_to_packedint
from pygame import Surface
import pygame


class Palette:
    def __init__(
        self,
        name: str,
        colors: list[RGBA],
        x: int,
        y: int,
        width: int,
        cell_size: int = 20,
    ):
        """Create a Palette pygame object

        Args:
            name (str): Name of the palette
            colors (list[RGBA]): List of RGBA colors in the palette
            x (int): X position of the palette
            y (int): Y position of the palette
            width (int): Width of the palette
            cell_size (int, optional): Size of each color cell in the palette. Defaults to 20.
        """
        # Meta info
        self.name: str = name

        # Palette info
        self.colors: list[RGBA] = colors
        self.selected: int = 0

        # Pos and Size data
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.cell_size: int = cell_size
        self.cells_per_row: float = width // cell_size
        self.rows: int = int(
            len(colors) // self.cells_per_row
            + (1 if len(colors) % self.cells_per_row > 0 else 0)
        )
        self.height: int = int(self.rows * cell_size)

        # Pygame relevant
        self.palette_surface: Surface = Surface((width, self.height))
        self.surfaces: list[Surface] = [None for _ in range(len(colors))]

    def __getitem__(self, index: int) -> RGBA:
        return self.colors[index]

    def __setitem__(self, index: int, value: RGBA):
        self.colors[index] = value
        self._update_surfaces()

    def add_color(self, color: RGBA):
        """Add a new color to the palette

        Args:
            color (RGBA): Color to add
        """
        self.colors.append(color)
        self.surfaces.append(None)
        self._update_surfaces()

    def _recalculate_height(self):
        """Recalculate the height of the palette based on the number of colors"""
        self.rows = len(self.colors) // self.cells_per_row + (
            1 if len(self.colors) % self.cells_per_row > 0 else 0
        )
        self.height = self.rows * self.cell_size
        self.palette_surface = Surface((self.width, self.height))

    def _update_surfaces(self):
        """Update the surfaces for each color in the palette"""
        for i, color in enumerate(self.colors):
            if self.surfaces[i] is None:
                self.surfaces[i] = Surface((self.width, self.height))
            self.surfaces[i].fill(color)

    def select(self, index: int):
        """Select a color at the specified index

        Args:
            index (int): Index of the color to select
        """
        if index < 0 or index >= len(self.colors):
            return
        self.selected = index

    def select_return(self, index: int, setter: callable):
        """Select a color at the specified index and call a setter function

        Args:
            index (int): Index of the color to select
            setter (callable): Function to call with the selected color
        """
        if index < 0 or index >= len(self.colors):
            return
        self.selected = index
        setter(self.colors[index])

    def click(self, x: int, y: int):
        if x < self.x or x > self.width:
            return
        if y < self.y or y > self.height:
            return

        # Calculate the index of the clicked color


class ColorSelector:
    def __init__(
        self,
        x: int,
        y: int,
        size: tuple[float, float] = (100.0, 100.0),
        hue_picker_height: float = 10.0,
        hue_picker_padding: float = 5.0,
    ):
        """Create a ColorSelector pygame object

        Args:
            x (int): X position of the color picker
            y (int): Y position of the color picker
            size (tuple[float, float], optional): Scale of the color picker. Defaults to (100.0, 100.0)
            hue_picker_height (float, optional): Height of the hue picker. Defaults to 10.0.
            hue_picker_padding (float, optional): Padding between the SV picker and the hue picker. Defaults to 5.0.
        """
        self.x: int = x
        self.y: int = y
        self.size: tuple[float, float] = size
        self.color: RGBA = (0, 0, 0, 255)
        self.sv_surface: Surface = Surface((SATURATION_MAX + 1, VALUE_MAX + 1))
        self.hue = 0
        self.sat = 0
        self.val = 0
        self.update_hue(0)

        self.hue_surface: Surface = Surface((HUE_MAX + 1, 1))
        self.hue_picker_height: float = hue_picker_height
        self.hue_picker_padding: float = hue_picker_padding

        self.color_display: Surface = Surface((size[0], hue_picker_height))

        self.calculate_hue_surface()

    def set_position(self, x: int, y: int):
        """Set the position of the color picker

        Args:
            x (int): New X position
            y (int): New Y position
        """
        self.x = x
        self.y = y

    def set_size(self, x: float, y: float):
        """Set the size of the color picker

        Args:
            x (float): New width of the color picker
            y (float): New height of the color picker
        """
        self.size = (x, y)
        self.calculate_hue_surface()
        self.update_hue(self.hue)
        self.update_color_display()

    def calculate_hue_surface(self):
        pixel_array = pygame.surfarray.pixels2d(self.hue_surface)
        for x in range(HUE_MAX + 1):
            hsv: HSV = (x, SATURATION_MAX, VALUE_MAX)
            rgb: RGB = hsva_to_rgba(hsv, 255)[:3]
            pos = (x, 0)
            pixel_array[pos] = rgb_to_packedint(rgb)
        del pixel_array  # Unlock the surface

    def update_hue(self, hue: int):
        """Update the color picker surface with a new hue
        Args:
            hue (int): Hue value from 0 to 360
        """
        self.hue = hue
        if hue < 0 or hue > HUE_MAX:
            return

        pixel_array = pygame.surfarray.pixels2d(self.sv_surface)
        height, width = VALUE_MAX, SATURATION_MAX

        for y in range(height + 1):
            for x in range(width + 1):
                hsv: HSV = (hue, x, y)
                rgb: RGB = hsva_to_rgba(hsv, 255)[:3]
                pos = (x, VALUE_MAX - y)
                pixel_array[pos] = rgb_to_packedint(rgb)

        del pixel_array  # Unlock the surface

    def update_color_display(self):
        self.color_display: Surface = Surface((self.size[0], self.hue_picker_height))
        self.color_display.fill(self.color)

    def draw(self, surface: Surface):
        """Draw the color picker onto a given surface

        Args:
            surface (Surface): The Pygame surface to draw the color picker onto
        """

        # Draw SV Picker
        scaled_sv_surface = pygame.transform.scale(self.sv_surface, self.size)
        surface.blit(scaled_sv_surface, (self.x, self.y))

        # Draw Hue picker
        scaled_hue_surface = pygame.transform.scale(
            self.hue_surface, (self.size[0], self.hue_picker_height)
        )
        surface.blit(
            scaled_hue_surface,
            (self.x, self.y + self.size[1] + self.hue_picker_padding),
        )
        surface.blit(
            self.color_display,
            (
                self.x,
                self.y
                + self.size[1]
                + self.hue_picker_height
                + self.hue_picker_padding * 2,
            ),
        )

    def click(self, x: int, y: int, func: callable = None) -> RGBA:
        """Handle a click event on the color picker
        Args:
            x (int): X coordinate of the click
            y (int): Y coordinate of the click
            func (callable, optional): Function to call with the selected color. Defaults to None.
        Returns:
            RGBA: The selected color in RGBA format
            Bool: True if the anything was clicked/changed, False otherwise
        """
        x -= self.x
        y -= self.y

        # Hue Picker
        if (
            y > self.size[1] + self.hue_picker_padding
            and y < self.size[1] + self.hue_picker_height + self.hue_picker_padding
            and 0 <= x <= self.size[0]
        ):
            x = round((x / self.size[0]) * HUE_MAX)
            if x <= HUE_PICKER_TOLERANCE:
                x = 0

            elif x >= HUE_MAX - HUE_PICKER_TOLERANCE:
                x = HUE_MAX

            self.update_hue(x)

            return self.color, True

        if x < 0 or x > self.size[0] or y < 0 or y > self.size[1]:
            return self.color, False

        # SV Picker
        y = self.size[1] - y  # Invert y-axis for correct color mapping

        h = self.hue

        s = round((x / self.size[0]) * SATURATION_MAX)
        v = round((y / self.size[1]) * VALUE_MAX)

        if s >= SATURATION_MAX - COLOR_PICKER_TOLERANCE:
            s = SATURATION_MAX
        elif s <= COLOR_PICKER_TOLERANCE:
            s = 0

        if v >= VALUE_MAX - COLOR_PICKER_TOLERANCE:
            v = VALUE_MAX
        elif v <= COLOR_PICKER_TOLERANCE:
            v = 0

        self.sat = s
        self.val = v

        self.color = hsva_to_rgba((h, s, v), 255)

        self.color_display.fill(self.color)

        if func:
            func(self.color)

        return self.color, True
