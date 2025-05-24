from random import randint
import pygame
from pygame.locals import QUIT
import pixilib.Camera as Camera
from pixilib.Grid import ComputedLayeredGrid, Grid


def main():
    # Initialize Pygame
    pygame.init()
    # Create a window
    screen = pygame.display.set_mode((800, 600))

    clock = pygame.time.Clock()

    # Create a grid and camera
    layer1 = Grid(16, 16)
    grid = ComputedLayeredGrid(16, 16)
    grid.add_layer(layer1)
    camera = Camera.GridCamera(grid, 160, 160, 320, 320)
    cam_surface = pygame.Surface((grid.width, grid.height))

    # Main loop
    running = True

    while running:
        dt = clock.tick(60)

        keys_held = pygame.key.get_pressed()
        mouse_held = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        if keys_held[pygame.K_r]:
            # Reset

            grid.clear()

        if mouse_held[0]:
            camera.click(mouse_pos[0], mouse_pos[1], cam_surface, 0)
        # Clear the screen
        screen.fill((31, 31, 31))

        # Draw the grid using the camera
        camera.draw(screen, cam_surface, (255, 255, 255))

        # Update the display
        pygame.display.flip()

    quit()


main()
