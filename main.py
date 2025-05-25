from typing import Dict
import pygame
from pygame.locals import *
from pygame.font import Font
import pixilib.Camera as Camera
from pixilib.Grid import ComputedLayeredGrid, Grid
from pixilib.DebugView import drawDebugView
from pixilib.Tools import *
from pixilib.Helpers import clamp, overflow, on_screen, in_grid


def main():
    # Initialize Pygame
    pygame.init()

    # Create a window
    screen_size = (800, 800)
    screen = pygame.display.set_mode(screen_size)

    clock = pygame.time.Clock()

    # Create a grid and camera
    layer1 = Grid(16, 16)
    grid = ComputedLayeredGrid(16, 16)
    grid.add_layer(layer1)
    camera_size = 320
    camera = Camera.GridCamera(
        grid,
        screen_size[0] / 2 - camera_size / 2,
        screen_size[1] / 2 - camera_size / 2,
        320,
        320,
    )
    cam_surface = pygame.Surface((grid.width, grid.height))

    # Main loop
    running = True

    font: Font = Font(None, 24)

    toolset: list[Tool] = mouse_held_tools + mouse_up_tools + mouse_pressed_tools
    selected_tool: int = 0

    tool_color: list[RGBA] = [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (0, 0, 0, 255),
    ]
    selected_color: int = 0

    tool_size: int = 0

    tool_brush_types: list[BrushTypes] = [
        BrushTypes.DEFAULT,
        BrushTypes.CIRCLE,
        BrushTypes.SQUARE,
    ]
    selected_brush: int = 0

    debug_text: Dict[str:any] = {
        "dt": 0,
        "Tool": lambda: toolset[selected_tool],
        "Color": lambda: tool_color[selected_color],
        "Tool Size": lambda: tool_size,
        "Brush Type": lambda: tool_brush_types[selected_brush].name,
    }

    pan_origin: tuple[int, int] = (0, 0)
    click_origin: tuple[int, int] = (0, 0)

    data = {"x": None, "y": None, "mouse_held": False}

    while running:
        dt = clock.tick(60)
        debug_text["dt"] = dt

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
                debug_text["Key Pressed"] = (
                    chr(event.key) if event.key < 0x10FFFF else event.key
                )

                if event.key == K_RIGHT:
                    selected_tool = overflow(selected_tool + 1, 0, len(toolset))
                if event.key == K_LEFT:
                    selected_tool = overflow(selected_tool - 1, 0, len(toolset))

                if event.key == K_UP:
                    selected_color = overflow(selected_color + 1, 0, len(tool_color))
                if event.key == K_DOWN:
                    selected_color = overflow(selected_color - 1, 0, len(tool_color))

                if event.key == K_KP_PLUS:
                    tool_size = overflow(tool_size + 1, 0, 11)
                if event.key == K_KP_MINUS:
                    tool_size = overflow(tool_size - 1, 0, 11)

                if event.key == K_KP_MULTIPLY:
                    selected_brush = overflow(
                        selected_brush + 1, 0, len(tool_brush_types)
                    )
                if event.key == K_KP_DIVIDE:
                    selected_brush = overflow(
                        selected_brush - 1, 0, len(tool_brush_types)
                    )

            if event.type == MOUSEBUTTONDOWN:
                debug_text["Mouse Pressed"] = event.button

                pan_origin = mouse_pos
                click_origin = (grid_x, grid_y)

                debug_text["Pan Origin"] = pan_origin
                debug_text["Click Origin"] = click_origin

                if toolset[selected_tool] in mouse_pressed_tools:
                    if in_grid(grid_x, grid_y, grid.width, grid.height):
                        toolset[selected_tool].run(
                            x=grid_x,
                            y=grid_y,
                            grid=grid,
                            color=tool_color[selected_color],
                            radius=tool_size,
                            radius_type=tool_brush_types[selected_brush],
                            data=data,
                            mouse_held=mouse_held[0],
                        )

            if event.type == MOUSEBUTTONUP:
                debug_text["Mouse Pressed"] = None
                data["mouse_held"] = False
                if toolset[selected_tool] in mouse_up_tools:
                    if in_grid(grid_x, grid_y, grid.width, grid.height):
                        toolset[selected_tool].run(
                            x=click_origin[0],
                            y=click_origin[1],
                            x2=grid_x,
                            y2=grid_y,
                            grid=grid,
                            color=tool_color[selected_color],
                            radius=tool_size,
                            radius_type=tool_brush_types[selected_brush],
                            data=data,
                            mouse_held=mouse_held[0],
                        )

        # Left mouse
        if (
            mouse_held[0]
            and on_screen(*mouse_pos, screen.get_width(), screen.get_height())
            and in_grid(grid_x, grid_y, grid.width, grid.height)
        ):
            data["mouse_held"] = True

            if toolset[selected_tool] in mouse_held_tools:
                toolset[selected_tool].run(
                    x=grid_x,
                    y=grid_y,
                    x2=grid_x,
                    y2=grid_y,
                    grid=grid,
                    color=tool_color[selected_color],
                    radius=tool_size,
                    radius_type=tool_brush_types[selected_brush],
                    data=data,
                    mouse_held=mouse_held[0],
                )

        # Middle mouse
        if mouse_held[1]:
            # Pan the camera
            dx = mouse_pos[0] - pan_origin[0]
            dy = mouse_pos[1] - pan_origin[1]
            camera.set_position(camera.real_x + dx, camera.real_y + dy)
            pan_origin = mouse_pos
            data["mouse_held"] = True

        # Clear the screen
        screen.fill((31, 31, 31))

        # Draw the grid using the camera
        camera.draw(screen, cam_surface, (255, 255, 255))

        # Update tool data
        for tool in toolset:
            tool.update(x=grid_x, y=grid_y, data=data, mouse_held=mouse_held[0])

        if toolset[selected_tool] == PaintTool or toolset[selected_tool] == EraserTool:
            data["x"] = grid_x
            data["y"] = grid_y

        # Draw debug information
        drawDebugView(font, screen, (255, 255, 255), debug_text)

        # Update the display
        pygame.display.flip()

    quit()


main()
