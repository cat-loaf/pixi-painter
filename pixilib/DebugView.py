from pygame import Surface, Color, draw
from pygame.font import Font
from .Types import RGB, RGBA
from matplotlib.colors import XKCD_COLORS


def drawDebugView(font: Font, screen: Surface, color: RGB, texts: dict):
    texts = {k: v for k, v in texts.items() if v is not None}
    for label, value in texts.items():
        if callable(value):
            value = value()

        if isinstance(value, type(RGB)) or isinstance(value, type(RGBA)):
            value = f"{value} - {XKCD_COLORS.get(value, 'Unknown Color')}"

        text_surface = font.render(f"{label}: {value.__str__()}", True, color)
        # draw from bottom right to top right
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (
            screen.get_width() - 10,
            screen.get_height() - 10 - list(reversed(texts.keys())).index(label) * 20,
        )
        screen.blit(text_surface, text_rect)
