import pygame
from pygame.locals import *
from pygame.font import Font
import pixilib.Camera as Camera
from pixilib.Grid import ComputedLayeredGrid, Grid
from pixilib.DebugView import drawDebugView
from pixilib.Tools import *


def main():
    # Initialize Pygame
    pygame.init()
    # Create a window
    screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()

    # Create a grid and camera
    layer1 = Grid(16, 16)
    grid = ComputedLayeredGrid(16, 16)
    grid.add_layer(layer1)
    camera = Camera.GridCamera(grid, 160, 160, 320, 320)
    cam_surface = pygame.Surface((grid.width, grid.height))

    # Main loop
    running = True

    font: Font = Font(None, 24)

    toolset: list[Tool] = mouse_held_tools + mouse_pressed_tools
    selected_tool: int = 0

    tool_color: list[RGBA] = [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (0, 0, 0, 255),
    ]
    selected_color: int = 0

    debug_texts = {
        "dt": 0,
        "Tool": lambda: toolset[selected_tool],
        "Color": lambda: tool_color[selected_color],
    }
    while running:
        dt = clock.tick(60)
        debug_texts["dt"] = dt

        keys_held = pygame.key.get_pressed()
        mouse_held = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        grid_increment = camera.width // camera.grid.width
        grid_x = int((mouse_pos[0] - camera.real_x) / grid_increment)
        grid_y = int((mouse_pos[1] - camera.real_y) / grid_increment)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    # Switch to next tool
                    selected_tool = (selected_tool + 1) % len(toolset)
                if event.key == K_LEFT:
                    # Switch to previous tool
                    selected_tool = (selected_tool - 1) % len(toolset)

                if event.key == K_UP:
                    # Switch to next color
                    selected_color = (selected_color + 1) % len(tool_color)
                if event.key == K_DOWN:
                    # Switch to previous color
                    selected_color = (selected_color - 1) % len(tool_color)

            if event.type == MOUSEBUTTONDOWN:
                debug_texts["Mouse Pressed"] = event.button
                if toolset[selected_tool] in mouse_pressed_tools:
                    if 0 <= grid_x < grid.width and 0 <= grid_y < grid.height:
                        toolset[selected_tool].run(
                            x=grid_x,
                            y=grid_y,
                            grid=grid,
                            color=tool_color[selected_color],
                            radius=0,
                        )
            else:
                debug_texts["Mouse Pressed"] = None

        if mouse_held[0]:
            if 0 <= grid_x < grid.width and 0 <= grid_y < grid.height:
                if toolset[selected_tool] in mouse_held_tools:
                    toolset[selected_tool].run(
                        x=grid_x,
                        y=grid_y,
                        grid=grid,
                        color=tool_color[selected_color],
                        radius=0,
                    )
            # camera.click(mouse_pos[0], mouse_pos[1], cam_surface, 0)
        # Clear the screen
        screen.fill((31, 31, 31))

        # Draw the grid using the camera
        camera.draw(screen, cam_surface, (255, 255, 255))

        # Draw debug information
        drawDebugView(font, screen, (255, 255, 255), debug_texts)

        # Update the display
        pygame.display.flip()

    quit()


main()
