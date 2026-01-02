from character import Character
from grid import GameGrid, GameBoard
import pygame, sys
from simulator import * 
from util import log

from windows.main_menu import MainMenu

def main():

    pygame.init()
    """
    r_game_grid = GameGrid()
    b_game_grid = GameGrid()


    r_1 = Character.characterFromId('001')
    r_2 = Character.characterFromId('002')
    b_1 = Character.characterFromId('003')
    b_2 = Character.characterFromId('001')
    b_3 = Character.characterFromId('004')

    r_game_grid.setCharacter(r_1, "front", 2)
    r_game_grid.setCharacter(r_2, "middle", 2)

    b_game_grid.setCharacter(b_1, "back", 1)
    b_game_grid.setCharacter(b_2, "front", 2)
    b_game_grid.setCharacter(b_3, "back", 3)

    game_board = GameBoard(r_game_grid, b_game_grid)

    attackSimulator(game_board)
    log.saveLog()  
    """
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Main Menu Example")

    main_menu = MainMenu(screen, buttons=[])
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_pos = pygame.mouse.get_pos()
        main_menu.update(mouse_pos)

        screen.fill((255, 255, 255))
        main_menu.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()