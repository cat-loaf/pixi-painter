import pygame
from .Grid import Grid, ComputedLayeredGrid
from pygame import Surface
from .Helpers import rgb_to_packedint, rgba_to_rgb
from .Types import RGB
from .Tools import Tool, PaintTool


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
        self.scale: float = scale

        self.scale_dirty: bool = True
        self.scaled_surface: Surface = Surface((1, 1))

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
        # set scale up to two decimal places
        self.scale = round(scale, 2)
        self.scale_dirty = True

    def draw(
        self,
        screen: Surface,
        surface: Surface,
        background: RGB,
        draw_gridlines: bool = True,
    ):
        """Draw the grid onto the surface, scaling it to fit the camera dimensions

        Args:
            screen (Surface): The Pygame screen to draw on
            surface (Surface): The surface to draw the grid onto
            background (RGB): The background color to fill the surface with (needed for RGBA to RGB conversion)
        """

        surface.fill(background)

        # Convert grid to surface (performantly)
        self._generate_surface(surface, background)

        # Draw overlay grid
        self.draw_overlay_grid(screen, surface)

        # Scale the surface to camera dimensions
        # self.scaled_surface =
        self._scale_surface_to_camera_dimensions(surface, self.width, self.height)

        if self.scale >= 0.91:
            self._draw_gridlines(
                self.scaled_surface, (0, 0, 0), draw_gridlines
            )  # Draw grid lines on the surface

        screen.blit(
            self.scaled_surface,
            (
                int(self.real_x),
                int(self.real_y),
            ),
        )

    def draw_overlay_grid(self, screen: Surface, surface: Surface):
        """Draw the overlay grid onto the surface, scaling it to fit the camera dimensions

        Args:
            screen (Surface): The Pygame screen to draw on
            surface (Surface): The surface to draw the overlay grid onto
        """
        # grid_increment_x = (self.width // self.grid.width) * self.scale
        # grid_increment_y = (self.height // self.grid.height) * self.scale

        # for grid_y, row in enumerate(self.grid.overlay.cells):
        #     for grid_x, cell in enumerate(row):
        #         if cell.value[3] > 0:
        #             pygame.draw.rect(
        #                 surface,
        #                 rgba_to_rgb(cell.value, self.grid[grid_x, grid_y].value),
        #                 (
        #                     cell.x * grid_increment_x,
        #                     cell.y * grid_increment_y,
        #                     self.width / self.grid.overlay.width * self.scale,
        #                     self.height / self.grid.overlay.height * self.scale,
        #                 ),
        #             )
        pixel_array = pygame.surfarray.pixels2d(surface)
        for y in range(self.grid.overlay.height):
            for x in range(self.grid.overlay.width):
                if self.grid.overlay.cells[y][x].value[3] == 0:
                    continue
                color = rgb_to_packedint(
                    rgba_to_rgb(
                        self.grid.overlay.cells[y][x].value,
                        (0, 0, 0),  # Default background color for overlay
                    )
                )
                pixel_array[x, y] = color

    def zoom_on(self, origin: tuple[float, float], scale: float):
        """Zoom the camera on a fixed point

        Args:
            origin (tuple[float, float]): The fixed point to zoom in on
            scale (float): The new scale factor
        """
        # Get offset
        dx = origin[0] - self.real_x
        dy = origin[1] - self.real_y

        # Get ratio of new scale to old scale
        scale_ratio = scale / self.scale

        # Adjust camera pos so origin stays fixed
        new_real_x = origin[0] - dx * scale_ratio
        new_real_y = origin[1] - dy * scale_ratio

        # Apply scale and pos
        self.set_scale(scale)
        self.set_position(new_real_x, new_real_y)

    def _generate_surface(
        self, surface: Surface, background: RGB, backgrounds: list[RGB] = None
    ):
        """Internal Method, Generate surface from grid data
        Writes pixel data directly to the surface's pixel array for performance

        Args:
            surface (Surface): The Pygame surface to draw the grid onto
            background (RGB): The background color to fill the surface with, used for RGBA to RGB conversion
            backgrounds (list[RGB], optional): List of background colors for each layer. Will use backgrounds if provided. Defaults to None.
        """
        pixel_array = pygame.surfarray.pixels2d(surface)
        grid = self.grid.get_computed_grid()  # Avoid repeated access
        use_layer_backgrounds = backgrounds is not None
        height, width = self.grid.height, self.grid.width

        for y in range(height):
            bg_row = backgrounds[y] if use_layer_backgrounds else None
            for x in range(width):
                rgba = grid[x, y].value
                bg_color = bg_row[x].value if use_layer_backgrounds else background
                rgb = rgba_to_rgb(rgba, bg_color)
                pixel_array[x, y] = rgb_to_packedint(rgb)

        del pixel_array  # Unlock the surface

    def _scale_surface_to_camera_dimensions(
        self, surface: Surface, width: int, height: int
    ) -> Surface:
        """Internal Method, Scale the surface to fit the camera dimensions

        Args:
            surface (Surface): The Pygame surface to scale
            width (int): Width of the scaled surface
            height (int): Height of the scaled surface

        Returns:
            Surface: _description_
        """
        # return
        if self.scale_dirty:
            self.scaled_surface = Surface((width * self.scale, height * self.scale))
            self.scale_dirty = False
        pygame.transform.scale(
            surface, (width * self.scale, height * self.scale), self.scaled_surface
        )

    def _draw_gridlines(self, surface: Surface, color: RGB, draw: bool = True):
        """Internal Method, Draw grid lines on the surface

        Args:
            surface (Surface): The Pygame surface to draw the grid lines on
            color (RGB): The color of the grid lines
        """
        if not draw:
            return

        if self.scale < 0.91:
            return

        grid_incr = (self.width // self.grid.width) * self.scale

        if grid_incr < 5.0:
            return

        horizontal_grid_lines = [x * grid_incr for x in range(self.grid.width + 1)]
        vertical_grid_lines = [y * grid_incr for y in range(self.grid.height + 1)]
        for x in horizontal_grid_lines[: self.grid.width + 1]:
            pygame.draw.line(surface, color, (x, 0), (x, self.height * self.scale))
        for y in vertical_grid_lines[: self.grid.height + 1]:
            pygame.draw.line(surface, color, (0, y), (self.width * self.scale, y))
