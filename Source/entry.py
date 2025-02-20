import pygame

from Source.lib import global_data
from Source.lib import handle_events
from Source.lib.ui import toolbar 
from Source.lib.ui.buttons import *

manager = global_data.PygameGlobals()

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

while manager.running:
    handle_events.handle_events(manager)

    manager.draw()        
    manager.clock.tick(60)

# End of game loop
pygame.quit()