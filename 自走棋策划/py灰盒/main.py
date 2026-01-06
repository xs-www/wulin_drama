#from character import Character
from grid import GameGrid, GameBoard
import pygame, sys
from simulator import * 
from util import log, em
from entity import Damage, Character


from windows.main_menu import MainMenu

def main():

    pygame.init()

    r_game_grid = GameGrid()
    b_game_grid = GameGrid()


    r_1 = Character.byId('0002')
    r_2 = Character.byId('0002')
    b_1 = Character.byId('0002')
    b_2 = Character.byId('0003')
   
    r_game_grid.setCharacter(r_1, "front", 1)
    r_game_grid.setCharacter(r_2, "front", 2)

    b_game_grid.setCharacter(b_1, "front", 1)
    b_game_grid.setCharacter(b_2, "middle", 1)

    game_board = GameBoard(r_game_grid, b_game_grid)
    generateActionList(game_board)

    #r_1.getHurt(Damage(amount=3, damage_type="physical", source=b_2))
    log.saveLog()  

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()