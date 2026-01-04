#from character import Character
from grid import GameGrid, GameBoard
import pygame, sys
from simulator import * 
from util import log, em
from entity import Damage, Character
from effect import Effect, Buff

from windows.main_menu import MainMenu

def main():

    pygame.init()

    r_game_grid = GameGrid()
    b_game_grid = GameGrid()


    r_1 = Character.byId('0002')
    r_2 = Character.byId('0003')
    b_1 = Character.byId('0003')
    b_2 = Character.byId('0005')
    b_3 = Character.byId('0004')

    r_game_grid.setCharacter(r_1, "front", 2)
    r_game_grid.setCharacter(r_2, "middle", 2)

    b_game_grid.setCharacter(b_1, "back", 1)
    b_game_grid.setCharacter(b_2, "front", 2)
    b_game_grid.setCharacter(b_3, "back", 3)

    game_board = GameBoard(r_game_grid, b_game_grid)
    attackSimulator(game_board)

    #r_1.getHurt(Damage(amount=3, damage_type="physical", source=b_2))
    log.saveLog()  

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()