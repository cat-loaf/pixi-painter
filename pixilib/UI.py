from pygame import draw, Surface
from .Types import UI_BACKING, UI_BORDER
from .Images import ToolAssets
from .Helpers import coords_in

op = 20
ip = 10
ics = 32


def draw_ui_rects(
    screen: Surface,
    ui_locations: list[tuple[int, int, int, int, int, int]] = None,
):
    for x, y, width, height, line_width, border in ui_locations:
        draw.rect(screen, UI_BACKING, (x, y, width, height), line_width)
        if border > 0:
            draw.rect(screen, UI_BORDER, (x, y, width, height), border)


def draw_tool_icons(
    tool_icons: ToolAssets,
    screen: Surface,
    screen_width: int,
    screen_height: int,
    clicked_tool: str,
):
    tool_icons.select_tool(clicked_tool)

    x1 = screen_width - op - ics
    x0 = x1 - ip - ics

    y0 = op
    y1 = y0 + ip + ics
    y2 = y1 + ip + ics
    y3 = y2 + ip + ics

    screen.blit(tool_icons.paintbrush.get_image(), (x0, y0))
    screen.blit(tool_icons.eraser.get_image(), (x1, y0))

    screen.blit(tool_icons.line.get_image(), (x0, y1))
    screen.blit(tool_icons.fill.get_image(), (x1, y1))

    screen.blit(tool_icons.clear.get_image(), (x0, y2))
    screen.blit(tool_icons.pan.get_image(), (x1, y2))

    screen.blit(tool_icons.eyedropper.get_image(), (x0, y3))


def select_tool(
    mouse_x: int,
    mouse_y: int,
    screen_width: int,
    screen_height: int,
) -> str | None:
    x1 = screen_width - op - ics
    x0 = x1 - ip - ics

    y0 = op
    y1 = y0 + ip + ics
    y2 = y1 + ip + ics
    y3 = y2 + ip + ics

    if coords_in((mouse_x, mouse_y), (x0, y0, ics, ics)):
        return "paintbrush"
    elif coords_in((mouse_x, mouse_y), (x1, y0, ics, ics)):
        return "eraser"

    elif coords_in((mouse_x, mouse_y), (x0, y1, ics, ics)):
        return "line"
    elif coords_in((mouse_x, mouse_y), (x1, y1, ics, ics)):
        return "fill"

    elif coords_in((mouse_x, mouse_y), (x0, y2, ics, ics)):
        return "clear"
    elif coords_in((mouse_x, mouse_y), (x1, y2, ics, ics)):
        return "pan"

    elif coords_in((mouse_x, mouse_y), (x0, y3, ics, ics)):
        return "eyedropper"

    return None
