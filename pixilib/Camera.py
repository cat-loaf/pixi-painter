import pygame
from .Grid import Grid, ComputedLayeredGrid
from pygame import Surface
from .Helpers import rgb_to_packedint, rgba_to_rgb, RGB


class GridCamera:
    """A camera that renders a grid onto a surface, allowing for zoom and pan functionality"""

    def __init__(
        self,
        grid: ComputedLayeredGrid,
        real_x: int,
        real_y: int,
        real_width: int,
        real_height: int,
        scale: float = 1.0,
    ):
        # Draw grid based on camera position and scale
        self.grid = grid

        # Camera on Screen
        self.real_x: float = real_x  # Screen position
        self.real_y: float = real_y  # Screen position
        self.width: int = real_width  # Screen width
        self.height: int = real_height  # Screen height

        # Camera Viewport
        self.viewport_x: int = 0
        self.viewport_y: int = 0
        self.scale: float = scale

    def set_position(self, x: float, y: float):
        """Set camera position

        Args:
            x (float): Screen X position
            y (float): Screen Y position
        """
        self.real_x = x
        self.real_y = y

    def set_scale(self, scale: float):
        """Set camera scale

        Args:
            scale (float): Scale factor for the camera, where 1.0 is 100% zoom
        """
        self.scale = scale

    def draw(self, screen: Surface, surface: Surface, background: RGB):
        """Draw the grid onto the surface, scaling it to fit the camera dimensions

        Args:
            screen (Surface): The Pygame screen to draw on
            surface (Surface): The surface to draw the grid onto
            background (RGB): The background color to fill the surface with (needed for RGBA to RGB conversion)
        """

        surface.fill(background)

        # Convert grid to surface (performantly)
        self._generate_surface(surface, background)

        # Scale the surface to camera dimensions
        surface_scaled = self._scale_surface_to_camera_dimensions(
            surface, int(self.width * self.scale), int(self.height * self.scale)
        )

        screen.blit(
            surface_scaled,
            (
                int(self.real_x - self.viewport_x * self.scale),
                int(self.real_y - self.viewport_y * self.scale),
            ),
        )

    def _generate_surface(self, surface: Surface, background: RGB):
        """Generate surface from grid data
        Writes pixel data directly to the surface's pixel array for performance

        Args:
            surface (Surface): The Pygame surface to draw the grid onto
            background (RGB): The background color to fill the surface with, used for RGBA to RGB conversion
        """
        pixel_array = pygame.surfarray.pixels2d(surface)
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                color = rgb_to_packedint(
                    rgba_to_rgb(
                        self.grid.get_computed_grid()[x, y].value,
                        background,
                    )
                )
                pixel_array[x, y] = color
        del pixel_array

    def _scale_surface_to_camera_dimensions(
        self, surface: Surface, width: int, height: int
    ) -> Surface:
        """Scale the surface to fit the camera dimensions

        Args:
            surface (Surface): The Pygame surface to scale
            width (int): Width of the scaled surface
            height (int): Height of the scaled surface

        Returns:
            Surface: _description_
        """
        return pygame.transform.scale(surface, (width, height))

    def click(self, mouse_x, mouse_y, surface: Surface, layer: int = 0):
        """Handle mouse click events on the grid"""

        grid_increment = self.width / self.grid.width

        grid_x = int((mouse_x - self.real_x) / grid_increment)
        grid_y = int((mouse_y - self.real_y) / grid_increment)

        print(grid_x, grid_y)
        # check if the coordinates are within the grid bounds
        if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
            # get the cell at the clicked position
            self.grid[grid_x, grid_y] = (255, 0, 255, 255)
