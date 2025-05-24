from pygame import Surface, Color
from pygame.font import Font
from .Types import RGB


def drawDebugView(font: Font, screen: Surface, color: RGB, texts: dict):
    texts = {k: v for k, v in texts.items() if v is not None}
    for label, value in texts.items():
        if callable(value):
            value = value()

        text_surface = font.render(f"{label}: {value.__str__()}", True, color)
        screen.blit(text_surface, (10, 10 + list(texts.keys()).index(label) * 20))
