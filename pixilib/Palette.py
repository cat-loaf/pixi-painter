from .Types import RGBA
from pygame import Surface


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

    def click(self, x: int, y: int):
        if x < self.x or x > self.width:
            return
        if y < self.y or y > self.height:
            return

        # Calculate the index of the clicked color
