import pygame

from Source.lib import global_data
from Source.lib import handle_events

data = global_data.PygameGlobals()
while data.running:
    handle_events.handle_events(data)
    
    data.screen.fill((255,255,255))
    
    pygame.display.flip()
    
    data.clock.tick(60)

# End of game loop
pygame.quit()