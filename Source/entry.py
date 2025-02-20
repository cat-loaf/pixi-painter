import pygame

from Source.pixi import global_data
from Source.pixi import handle_events
from Source.pixi.ui import toolbar 
from Source.pixi.ui import palette
from Source.pixi.ui.buttons import *
from Source.pixi.io import palette_io

manager = global_data.PygameGlobals()
palette_file = palette_io.PaletteIO('palette.pal')
palette_file.write('palette.pal', manager.palette_colors)

manager.toolbar = toolbar.Toolbar(
    0, 0, 
    manager.screen_width, 
    50, 
    manager.colors['toolbar'], 
    manager
).add_buttons([
    ExitButton    (lambda : ( manager.get_width() - 24 - 6)                    , 13),
    MaximiseButton(lambda : ( manager.get_width() - 24 - 6 - 24 - 6)           , 13),
    MinimiseButton(lambda : ( manager.get_width() - 24 - 6 - 24 - 6 - 24 - 6)  , 13)
])

manager.palette = palette.Palette(
    0, 50, 
    24, 24, 
    colors=manager.palette_colors, 
    data=manager
)

while manager.running:
    handle_events.handle_events(manager)
    manager.draw()
    manager.clock.tick(60)

# End of game loop
pygame.quit()