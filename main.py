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
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    clock = pygame.time.Clock()

    canvas_size = (16, 9)
    camera_size = (canvas_size[0] * 20, canvas_size[1] * 20)

    # Create a grid and camera
    layer1 = Grid(canvas_size[0], canvas_size[1])
    grid = ComputedLayeredGrid(canvas_size[0], canvas_size[1])
    grid.add_layer(layer1)

    overlay_grid = Grid(canvas_size[0], canvas_size[1])
    grid.overlay = overlay_grid

    camera = Camera.GridCamera(
        grid,
        screen_size[0] / 2 - camera_size[0] / 2,
        screen_size[1] / 2 - camera_size[1] / 2,
        camera_size[0],
        camera_size[1],
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

    tool_sizes: list[int] = [0 for _ in range(len(toolset))]

    tool_brush_types: list[BrushTypes] = [
        BrushTypes.DEFAULT,
        BrushTypes.CIRCLE,
        BrushTypes.SQUARE,
    ]
    selected_brush: int = 0

    debug_text: Dict[str:any] = {
        "Screen Size": lambda: screen_size,
        "Tool": lambda: toolset[selected_tool],
        "Color": lambda: tool_color[selected_color],
        "Tool Size": lambda: tool_sizes[selected_tool],
        "Brush Type": lambda: tool_brush_types[selected_brush].name,
        "Camera Scale": lambda: camera.scale,
        "Camera Position": lambda: (camera.real_x, camera.real_y),
    }

    pan_origin: tuple[int, int] = (0, 0)
    click_origin: tuple[int, int] = (0, 0)

    data = {"x": None, "y": None, "mouse_held": False}

    while running:
        dt = clock.tick(60)

        keys_held = pygame.key.get_pressed()
        mouse_held = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # calculate grid increment based on camera scale grid size
        # grid_increment = camera.width // camera.grid.width
        # grid_x = int((mouse_pos[0] - camera.real_x) / grid_increment)
        # grid_y = int((mouse_pos[1] - camera.real_y) / grid_increment)
        grid_increment_x = (camera.width // grid.width) * camera.scale
        grid_increment_y = (camera.height // grid.height) * camera.scale
        canvas_mouse_x = mouse_pos[0] - camera.real_x
        canvas_mouse_y = mouse_pos[1] - camera.real_y

        grid_x = int(canvas_mouse_x // grid_increment_x)
        grid_y = int(canvas_mouse_y // grid_increment_y)

        debug_text["Grid Pos"] = (grid_x, grid_y)

        events = pygame.event.get()
        # debug_text["events"] = events
        for event in events:
            if event.type == VIDEORESIZE:
                screen_size = (event.w, event.h)

            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                debug_text["Key Pressed"] = (
                    chr(event.key) if event.key < 0x10FFFF else event.key
                )

                if event.key == K_RIGHT:
                    selected_tool = overflow(selected_tool + 1, 0, len(toolset) - 1)
                if event.key == K_LEFT:
                    selected_tool = overflow(selected_tool - 1, 0, len(toolset) - 1)

                if event.key == K_UP:
                    selected_color = overflow(
                        selected_color + 1, 0, len(tool_color) - 1
                    )
                if event.key == K_DOWN:
                    selected_color = overflow(
                        selected_color - 1, 0, len(tool_color) - 1
                    )

                if event.key == K_KP_PLUS:
                    tool_sizes[selected_tool] = clamp(
                        tool_sizes[selected_tool] + 1, 0, 10
                    )
                if event.key == K_KP_MINUS:
                    tool_sizes[selected_tool] = clamp(
                        tool_sizes[selected_tool] - 1, 0, 10
                    )

                if event.key == K_KP_MULTIPLY:
                    selected_brush = overflow(
                        selected_brush + 1, 0, len(tool_brush_types) - 1
                    )
                if event.key == K_KP_DIVIDE:
                    selected_brush = overflow(
                        selected_brush - 1, 0, len(tool_brush_types) - 1
                    )

            if event.type == MOUSEBUTTONDOWN:
                debug_text["Mouse Pressed"] = event.button

                pan_origin = mouse_pos

                debug_text["Pan Origin"] = pan_origin

                if event.button == 1:
                    click_origin = (grid_x, grid_y)
                    debug_text["Click Origin"] = click_origin
                    if toolset[selected_tool] in mouse_pressed_tools:
                        if in_grid(grid_x, grid_y, grid.width, grid.height):
                            toolset[selected_tool].run(
                                x=grid_x,
                                y=grid_y,
                                grid=grid,
                                color=tool_color[selected_color],
                                radius=tool_sizes[selected_tool],
                                radius_type=tool_brush_types[selected_brush],
                                data=data,
                                mouse_held=mouse_held[0],
                            )

            if event.type == MOUSEBUTTONUP:
                debug_text["Mouse Pressed"] = None
                data["mouse_held"] = False
                if event.button == 1:
                    if toolset[selected_tool] in mouse_up_tools:
                        if toolset[selected_tool] == LineTool:
                            LineTool.run(
                                x=click_origin[0],
                                y=click_origin[1],
                                x2=grid_x,
                                y2=grid_y,
                                grid=grid,
                                color=tool_color[selected_color],
                                radius=tool_sizes[selected_tool],
                                radius_type=tool_brush_types[selected_brush],
                                data=data,
                                mouse_held=mouse_held[0],
                            )
                        else:
                            if in_grid(grid_x, grid_y, grid.width, grid.height):
                                toolset[selected_tool].run(
                                    x=click_origin[0],
                                    y=click_origin[1],
                                    x2=grid_x,
                                    y2=grid_y,
                                    grid=grid,
                                    color=tool_color[selected_color],
                                    radius=tool_sizes[selected_tool],
                                    radius_type=tool_brush_types[selected_brush],
                                    data=data,
                                    mouse_held=mouse_held[0],
                                )

            # Scale camera with mouse wheel
            if event.type == MOUSEWHEEL:
                if event.y > 0:
                    camera.set_scale(clamp(camera.scale * 1.1, 0.1, 10.0))
                elif event.y < 0:
                    camera.set_scale(clamp(camera.scale / 1.1, 0.1, 10.0))

        # Left mouse
        if mouse_held[0]:
            if on_screen(
                *mouse_pos, screen.get_width(), screen.get_height()
            ) and in_grid(grid_x, grid_y, grid.width, grid.height):
                data["mouse_held"] = True

                if toolset[selected_tool] in mouse_held_tools:
                    toolset[selected_tool].run(
                        x=grid_x,
                        y=grid_y,
                        x2=grid_x,
                        y2=grid_y,
                        grid=grid,
                        color=tool_color[selected_color],
                        radius=tool_sizes[selected_tool],
                        radius_type=tool_brush_types[selected_brush],
                        data=data,
                        mouse_held=mouse_held[0],
                    )

            # Overlay for line tool (only active when mouse held)
            if toolset[selected_tool] == LineTool:
                LineTool.run(
                    grid=overlay_grid,
                    x=click_origin[0],
                    y=click_origin[1],
                    x2=grid_x,
                    y2=grid_y,
                    color=(
                        tool_color[selected_color][0],
                        tool_color[selected_color][1],
                        tool_color[selected_color][2],
                        100,
                    ),
                    radius=tool_sizes[selected_tool],
                    radius_type=tool_brush_types[selected_brush],
                    data=data,
                    mouse_held=mouse_held[0],
                )

        # Middle mouse
        if mouse_held[1]:
            # Pan the camera
            dx = mouse_pos[0] - pan_origin[0]
            dy = mouse_pos[1] - pan_origin[1]
            grid_width = camera.width * camera.scale
            grid_height = camera.height * camera.scale
            camera.set_position(
                clamp(
                    camera.real_x + dx,
                    grid_increment_x - grid_width,
                    screen_size[0] - grid_increment_x,
                ),
                clamp(
                    camera.real_y + dy,
                    grid_increment_y - grid_height,
                    screen_size[1] - grid_increment_y,
                ),
            )
            pan_origin = mouse_pos
            data["mouse_held"] = True

        # Overlay for tools
        if toolset[selected_tool] in mouse_preview_tools:
            if in_grid(grid_x, grid_y, grid.width, grid.height):
                overlay_grid[grid_x, grid_y] = (
                    tool_color[selected_color][0],
                    tool_color[selected_color][1],
                    tool_color[selected_color][2],
                    100,
                )

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

        # Clear overlay grid
        overlay_grid.clear((0, 0, 0, 0))

    quit()


main()
