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

    # Create a grid and camera
    layer1 = Grid(16, 16)
    grid = ComputedLayeredGrid(16, 16)
    grid.add_layer(layer1)
    camera = Camera.GridCamera(grid, 160, 160, 320, 320)
    cam_surface = pygame.Surface((grid.width, grid.height))

    # Main loop
    running = True

    while running:
        keys_pressed = pygame.key.get_pressed()
        mouse_left, mouse_middle, mouse_right = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if mouse_left:
                camera.click(event.pos[0], event.pos[1], cam_surface, 0)
            if event.type == QUIT:
                running = False

        # Clear the screen
        screen.fill((31, 31, 31))

        # Draw the grid using the camera
        camera.draw(screen, cam_surface, (255, 255, 255))

        # Update the display
        pygame.display.flip()

    quit()


main()
