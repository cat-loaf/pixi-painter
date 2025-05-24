from pygame import Surface, Color
from pygame.font import Font
from .Types import RGB


def drawDebugView(font: Font, screen: Surface, color: RGB, texts: dict):
    for label, value in texts.items():
        if value is None:
            continue

        if callable(value):
            value = value()

        text_surface = font.render(f"{label}: {value.__str__()}", True, color)
        screen.blit(text_surface, (10, 10 + list(texts.keys()).index(label) * 20))
