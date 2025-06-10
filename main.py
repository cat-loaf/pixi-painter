from typing import Dict

import pygame

from pygame.locals import *
from pygame.font import Font

from pixilib.Camera import GridCamera
from pixilib.Grid import ComputedLayeredGrid, Grid
from pixilib.DebugView import drawDebugView
from pixilib.Tools import *
from pixilib.Helpers import clamp, overflow, on_screen, in_grid, coords_in
from pixilib.Color import ColorSelector
from pixilib.Types import HUE_MAX, SATURATION_MAX
from pixilib.Images import ToolAssets, CursorAssets
from pixilib.UI import draw_ui_rects, draw_tool_icons, select_tool
from pixilib.UIWidgets import UIWidget, Label, TextInput
from pixilib.DataObject import DataObject as do


def main(debug=False):
    # Initialize Pygame
    pygame.init()

    # Create a window
    screen_size = (1000, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)
    cursor_assets = CursorAssets()
    cursor_image: pygame.Surface = cursor_assets.paint_cursor
    cursor_offset: tuple[int, int] = (0, 0)

    canvas_size = (64, 64)

    # calc cam proportion, then cam scale according to prop x and prop y
    cam_prop_x = canvas_size[0] / (canvas_size[0] + canvas_size[1])
    cam_prop_y = 1 - cam_prop_x
    cam_size_scale = max(
        1,
        int((480 / canvas_size[0]) * cam_prop_x + (480 / canvas_size[1]) * cam_prop_y),
    )
    camera_size = (canvas_size[0] * cam_size_scale, canvas_size[1] * cam_size_scale)

    # Create a grid and camera
    layer1 = Grid(canvas_size[0], canvas_size[1])
    grid = ComputedLayeredGrid(canvas_size[0], canvas_size[1])
    grid.add_layer(layer1)

    overlay_grid = Grid(canvas_size[0], canvas_size[1])
    overlay_transparency = 255
    grid.overlay = overlay_grid

    camera = GridCamera(
        grid,
        screen_size[0] / 2 - camera_size[0] / 2,
        screen_size[1] / 2 - camera_size[1] / 2,
        camera_size[0],
        camera_size[1],
    )
    cam_surface = pygame.Surface((grid.width, grid.height))

    color_selector = ColorSelector(
        x=15, y=15, size=[160, 160], hue_picker_height=20, hue_picker_padding=5
    )
    color_selector.click(color_selector.x + 158, color_selector.y + 1)

    hue_slots = 20
    hue_indicator = pygame.Surface(
        (color_selector.size[0] / hue_slots, color_selector.hue_picker_height),
        pygame.SRCALPHA,
    )
    sat_value_circle_percent = 0.1
    sat_val_indicator = pygame.Surface(
        (
            color_selector.size[0] * sat_value_circle_percent,
            color_selector.size[1] * sat_value_circle_percent,
        ),
        pygame.SRCALPHA,
    )

    pygame.draw.rect(
        hue_indicator,
        (0, 0, 0, 127),
        (0, 0, hue_indicator.get_width(), hue_indicator.get_height()),
        2,
    )

    pygame.draw.circle(
        sat_val_indicator,
        (0, 0, 0, 127),
        (sat_val_indicator.get_width() / 2, sat_val_indicator.get_height() / 2),
        sat_val_indicator.get_width() / 2,
        3,
    )

    tool_assets = ToolAssets()

    # Main loop
    running = True

    font: Font = Font(None, 24)

    # toolset: list[Tool] = (
    #     mouse_held_tools
    #     + mouse_up_tools
    #     + mouse_pressed_tools
    #     + mouse_preview_tools
    #     + mouse_other_tools
    # )
    selected_tool: int = 0

    tool_color: RGBA = (255, 0, 0, 255)

    tool_sizes: list[int] = [0 for _ in range(len(toolset))]

    tool_brush_types: list[BrushTypes] = [
        BrushTypes.DEFAULT,
        BrushTypes.CIRCLE,
        BrushTypes.SQUARE,
    ]
    selected_brush: int = 0

    dt: float = 0.0

    debug_text: Dict[str:any] = {
        "Δt": lambda: dt,
        "Tool": lambda: toolset[selected_tool],
        "Color": lambda: tool_color,
        "Tool Size": lambda: tool_sizes[selected_tool],
        "Brush Type": lambda: tool_brush_types[selected_brush].name,
        "Mouse Position": (0, 0),
        "Camera Scale": lambda: camera.scale,
        "Camera Position": lambda: (camera.real_x, camera.real_y),
        "Canvas Mouse": (0, 0),
    }

    pan_origin: tuple[int, int] = (0, 0)
    click_origin: tuple[int, int] = (0, 0)

    data = {"x": None, "y": None, "mouse_held": False}

    grid_cursor = pygame.Surface((17, 17), pygame.SRCALPHA)

    # (0, 0, 15 + color_selector_width + 15, screen_height, 0, 2),
    # (screen_width - op - ics - ip - ics - op, 0, screen_width, screen_height, 0, 2),

    op = 20
    ip = 10
    ics = 32

    ui_locations = [
        (0, 0, 15 + color_selector.size[0] + 15, screen_size[1], 0, 2),
        (
            screen_size[0] - op - ics - ip - ics - op,
            0,
            screen_size[0],
            screen_size[1],
            0,
            2,
        ),
    ]

    ui_widgets: dict[str, UIWidget] = {
        "label1": Label(
            text="Label 1",
            position=(300, 0),
            size=(0, 0),
            color=(255, 255, 255),
            font=font,
        ),
        "textInput1": TextInput(
            position=(300, 16 + 4),
            size=(64, 32),
            font=font,
            accepted_regex=r"[0-9]",
            max_chars=6,
            escape_callback=lambda: print(),
        ),
    }

    hovering_on: str = "None"

    draw_grid_overlay: bool = True

    focused_on: do = do("none")

    while running:
        dt = clock.tick(60)

        hovering_on: str = "none"

        keys_held = pygame.key.get_pressed()
        mouse_held = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # calculate grid increment based on camera scale grid size
        grid_incr = (camera.width // grid.width) * camera.scale
        debug_text["Grid Increment"] = grid_incr
        canvas_mouse_x = mouse_pos[0] - camera.real_x
        canvas_mouse_y = mouse_pos[1] - camera.real_y

        grid_x = int(canvas_mouse_x // grid_incr)
        grid_y = int(canvas_mouse_y // grid_incr)

        debug_text["Grid Pos"] = (grid_x, grid_y)

        events = pygame.event.get()

        tool_color = color_selector.color
        cursor_image, cursor_offset = cursor_assets.select_tool(
            toolset[selected_tool].__str__()
        )

        # Check where mouse hovering over
        if hovering_on == "none":
            for name, widget in ui_widgets.items():
                if isinstance(widget, UIWidget):
                    if coords_in(mouse_pos, (widget.x, widget.y, widget.w, widget.h)):
                        hovering_on = name
        if hovering_on == "none":
            for p in ui_locations:
                if coords_in(mouse_pos, (p[0], p[1], p[2], p[3])):
                    hovering_on = "ui"
        if hovering_on == "none":
            hovering_on = "canvas"

        if mouse_held[0]:
            focused_on.set_value(hovering_on)

        debug_text["Hovering On"] = hovering_on
        debug_text["Focused On"] = focused_on
        # Handle UI Clicks
        ui_clicked = False
        if mouse_held[0] and hovering_on != "canvas":
            ui_clicked = True
            ts = select_tool(mouse_pos[0], mouse_pos[1], screen_size[0], screen_size[1])
            if ts is not None:
                selected_tool = toolset_indexes.index(ts)

            # for x, y, widget, h, _, _ in ui_locations:
            #     if coords_in(mouse_pos, (x, y, widget, h)):
            #         ui_clicked = True
        debug_text["UI Clicked"] = ui_clicked

        # debug_text["events"] = events
        for event in events:
            if event.type == VIDEORESIZE:
                screen_size = (event.w, event.h)
                color_size = max(min([screen_size[0] // 5, screen_size[1] // 5]), 100)
                color_selector.set_size(color_size, color_size)
                ui_locations = [
                    (0, 0, 15 + color_selector.size[0] + 15, screen_size[1], 0, 2),
                    (
                        screen_size[0] - op - ics - ip - ics - op,
                        0,
                        screen_size[0],
                        screen_size[1],
                        0,
                        2,
                    ),
                ]

            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                debug_text["Key Pressed"] = (
                    chr(event.key) if event.key < 0x10FFFF else event.key
                )
                for name, widget in ui_widgets.items():
                    if isinstance(widget, TextInput):
                        if focused_on == name:
                            widget.receive_input(event.key, event.unicode)

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

                if event.key == K_g:
                    draw_grid_overlay = not draw_grid_overlay
                    debug_text["Draw Grid Overlay"] = draw_grid_overlay

            if event.type == MOUSEBUTTONDOWN:
                pan_origin = mouse_pos

                debug_text["Pan Origin"] = pan_origin

                if event.button == 1:
                    click_origin = (grid_x, grid_y)
                    debug_text["Click Origin"] = click_origin

                    for x, y, widget, h, _, _ in ui_locations:
                        if coords_in(mouse_pos, (x, y, widget, h)):
                            ui_clicked = True

                    if toolset[selected_tool] in mouse_pressed_tools and not ui_clicked:
                        if in_grid(grid_x, grid_y, grid.width, grid.height):
                            toolset[selected_tool].run(
                                x=grid_x,
                                y=grid_y,
                                grid=grid,
                                color=tool_color,
                                radius=tool_sizes[selected_tool],
                                radius_type=tool_brush_types[selected_brush],
                                data=data,
                                mouse_held=mouse_held[0],
                                color_selector=color_selector,
                            )

            if event.type == MOUSEBUTTONUP:
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
                                color=tool_color,
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
                                    color=tool_color,
                                    radius=tool_sizes[selected_tool],
                                    radius_type=tool_brush_types[selected_brush],
                                    data=data,
                                    mouse_held=mouse_held[0],
                                )

            # Scale camera with mouse wheel
            if event.type == MOUSEWHEEL:
                if event.y > 0:
                    # camera.set_scale(clamp(camera.scale * 1.1, 0.1, 10.0))
                    camera.zoom_on(
                        mouse_pos,
                        clamp(camera.scale * 1.1, 0.1, 10.0),
                    )
                elif event.y < 0:
                    # camera.set_scale(clamp(camera.scale / 1.1, 0.1, 10.0))
                    camera.zoom_on(
                        mouse_pos,
                        clamp(camera.scale / 1.1, 0.1, 10.0),
                    )
        debug_text["Mouse Position"] = mouse_pos
        debug_text["Canvas Mouse"] = (
            mouse_pos[0] - camera.real_x,
            mouse_pos[1] - camera.real_y,
        )

        # Left mouse
        if mouse_held[0] and not (keys_held[K_SPACE]):
            tool_color, clicked = color_selector.click(*mouse_pos)
            if not ui_clicked and not clicked:
                if on_screen(
                    *mouse_pos, screen.get_width(), screen.get_height()
                ) and in_grid(grid_x, grid_y, grid.width, grid.height):
                    if toolset[selected_tool] in mouse_held_tools:
                        toolset[selected_tool].run(
                            x=grid_x,
                            y=grid_y,
                            x2=grid_x,
                            y2=grid_y,
                            grid=grid,
                            color=tool_color,
                            radius=tool_sizes[selected_tool],
                            radius_type=tool_brush_types[selected_brush],
                            data=data,
                            mouse_held=True,
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
                            tool_color[0],
                            tool_color[1],
                            tool_color[2],
                            overlay_transparency,
                        ),
                        radius=tool_sizes[selected_tool],
                        radius_type=tool_brush_types[selected_brush],
                        data=data,
                        mouse_held=mouse_held[0],
                    )

        # Panning functionality
        if (
            mouse_held[1]
            or (toolset[selected_tool] == PanTool and mouse_held[0])
            or (keys_held[K_SPACE] and mouse_held[0])
        ) and (not ui_clicked):
            # Pan the camera
            dx = mouse_pos[0] - pan_origin[0]
            dy = mouse_pos[1] - pan_origin[1]
            grid_width = camera.width * camera.scale
            grid_height = camera.height * camera.scale
            camera.set_position(
                clamp(
                    camera.real_x + dx,
                    grid_incr - grid_width,
                    screen_size[0] - grid_incr,
                ),
                clamp(
                    camera.real_y + dy,
                    grid_incr - grid_height,
                    screen_size[1] - grid_incr,
                ),
            )
            pan_origin = mouse_pos
            data["mouse_held"] = True

        # Overlay for tools
        if toolset[selected_tool] == LineTool:
            LineTool.run(
                x=grid_x,
                y=grid_y,
                x2=grid_x,
                y2=grid_y,
                grid=overlay_grid,
                color=(
                    tool_color[0],
                    tool_color[1],
                    tool_color[2],
                    overlay_transparency,
                ),
                radius=(tool_sizes[selected_tool]),
                radius_type=BrushTypes.SQUARE,
                data=data,
                mouse_held=mouse_held[0],
                grid_type="Grid",
            )
        if toolset[selected_tool] in mouse_preview_tools:
            if in_grid(grid_x, grid_y, grid.width, grid.height):
                # overlay_grid[grid_x, grid_y] = (
                #     tool_color[selected_color][0],
                #     tool_color[selected_color][1],
                #     tool_color[selected_color][2],
                #     overlay_transparency,
                # )

                PaintTool.run(
                    x=grid_x,
                    y=grid_y,
                    grid=overlay_grid,
                    color=(
                        tool_color[0],
                        tool_color[1],
                        tool_color[2],
                        overlay_transparency,
                    ),
                    radius=(
                        tool_sizes[selected_tool]
                        if toolset[selected_tool] not in no_cursor_grid_preview
                        else 0
                    ),
                    radius_type=tool_brush_types[selected_brush],
                    data=data,
                    mouse_held=mouse_held[0],
                    grid_type="Grid",
                    use_executor=False,
                )

        # Clear the screen
        screen.fill((31, 31, 31))

        camera.draw(
            screen, cam_surface, (255, 255, 255), draw_gridlines=draw_grid_overlay
        )

        # Update tool data
        for tool in toolset:
            tool.update(x=grid_x, y=grid_y, data=data, mouse_held=mouse_held[0])

        if toolset[selected_tool] == PaintTool or toolset[selected_tool] == EraserTool:
            data["x"] = grid_x
            data["y"] = grid_y

        # Draw grid cursor
        if toolset[selected_tool] not in no_cursor_grid_preview and in_grid(
            grid_x, grid_y, grid.width, grid.height
        ):
            # recalc grid_x and grid_y in case camera move or zoom
            tmp_grid_x = grid_x
            tmp_grid_y = grid_y
            grid_x = int((mouse_pos[0] - camera.real_x) // grid_incr)
            grid_y = int((mouse_pos[1] - camera.real_y) // grid_incr)
            grid_cursor.fill((0, 0, 0, 0))  # Clear the grid cursor
            match tool_brush_types[selected_brush]:
                case BrushTypes.SQUARE:
                    pygame.draw.rect(grid_cursor, (127, 127, 127), (0, 0, 17, 17), 2)
                case BrushTypes.CIRCLE | _:
                    radius, width, color = (
                        8,
                        1 if tool_sizes[selected_tool] > 4 else 2,
                        (127, 127, 127),
                    )
                    pygame.draw.circle(
                        grid_cursor,
                        color,
                        (radius + 1, radius + 1),
                        radius,
                        width,
                        False,
                        False,
                        False,
                        True,
                    )
                    pygame.draw.circle(
                        grid_cursor,
                        color,
                        (radius, radius + 1),
                        radius,
                        width,
                        False,
                        False,
                        True,
                        False,
                    )
                    pygame.draw.circle(
                        grid_cursor,
                        color,
                        (radius, radius),
                        radius,
                        width,
                        False,
                        True,
                        False,
                        False,
                    )
                    pygame.draw.circle(
                        grid_cursor,
                        color,
                        (radius + 1, radius),
                        radius,
                        width,
                        True,
                        False,
                        False,
                        False,
                    )
                    pygame.draw.line(
                        grid_cursor, color, (radius, 0), (radius + width, 0), width
                    )  # top
                    pygame.draw.line(
                        grid_cursor,
                        color,
                        (radius, 17 - width),
                        (radius + width, 17 - width),
                        width,
                    )  # bottom
                    pygame.draw.line(
                        grid_cursor, color, (0, radius), (0, radius + width), width
                    )  # left
                    pygame.draw.line(
                        grid_cursor,
                        color,
                        (17 - width, radius),
                        (17 - width, radius + width),
                        width,
                    )  # right

            # Draw cursor plus
            cursor_grid_pos = (
                grid_x * grid_incr + camera.real_x,
                grid_y * grid_incr + camera.real_y,
            )
            camera_cell_size = camera.width // grid.width * camera.scale

            # center of scaled grid_cursor should be at center of mouse
            cell_size = 1
            grid_cursor_offset = tool_sizes[selected_tool] * camera_cell_size
            match tool_brush_types[selected_brush]:
                case BrushTypes.SQUARE:
                    match tool_sizes[selected_tool]:
                        case 0:
                            cell_size = 1
                            grid_cursor_offset = 0
                        case 1:
                            cell_size = 2
                        case _:
                            cell_size = tool_sizes[selected_tool] * 2 - 1
                            grid_cursor_offset = (
                                tool_sizes[selected_tool] - 1
                            ) * camera_cell_size

                case BrushTypes.CIRCLE | _:
                    cell_size = tool_sizes[selected_tool] * 2 + 1

            scaled_cell_size = camera_cell_size * cell_size
            scaled_grid_cursor = pygame.transform.scale(
                grid_cursor, (scaled_cell_size, scaled_cell_size)
            )

            screen.blit(
                scaled_grid_cursor,
                (
                    cursor_grid_pos[0] - grid_cursor_offset,
                    cursor_grid_pos[1] - grid_cursor_offset,
                ),
                special_flags=pygame.BLEND_SUB,
            )

            grid_x = tmp_grid_x
            grid_y = tmp_grid_y

        draw_ui_rects(screen, ui_locations)
        draw_tool_icons(
            tool_assets,
            screen,
            screen_size[0],
            screen_size[1],
            (toolset[selected_tool].__str__()),
        )

        # draw palette
        color_selector.draw(screen)
        screen.blit(
            hue_indicator,
            (
                color_selector.x
                + round((color_selector.hue / HUE_MAX) * color_selector.size[0]),
                color_selector.y
                + color_selector.size[1]
                + color_selector.hue_picker_padding,
            ),
        )
        screen.blit(
            sat_val_indicator,
            (
                color_selector.x
                + (color_selector.sat / SATURATION_MAX) * color_selector.size[0]
                - (sat_val_indicator.get_width() / 2),
                color_selector.y
                + ((SATURATION_MAX - color_selector.val) / SATURATION_MAX)
                * color_selector.size[1]
                - (sat_val_indicator.get_height() / 2),
            ),
        )

        # Draw UI widgets
        for widget in ui_widgets.values():
            widget.draw(screen)

        if debug:
            drawDebugView(font, screen, (255, 255, 255), debug_text)

        if cursor_image is not None:
            screen.blit(
                cursor_image,
                (
                    mouse_pos[0] - cursor_offset[0],
                    mouse_pos[1] - cursor_offset[1],
                ),
            )

        # Update display
        pygame.display.flip()

        # Clear overlay grid
        overlay_grid.clear((0, 0, 0, 0))

    quit()


# If the script is run with the argument "profile", use cProfile to profile the main function
from sys import argv

if "debug" in argv:
    main(debug=True)
elif "profile" in argv:
    import cProfile as profile

    profile.run("main()")
else:
    main()
    # from pixilib.Images import get_images

    # get_images()
