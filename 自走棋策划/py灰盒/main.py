#from character import Character
from grid import GameGrid, GameBoard
import pygame, sys
from simulator import * 
from util import log, em
from entity import Damage, Character
from keywords import *


from windows.main_menu import MainMenu

def main():

    pygame.init()

    r_game_grid = GameGrid()
    b_game_grid = GameGrid()

    r_1 = Character.byId('0002')
    r_1.draw()
    
    r_1.addKeyword("Sheild")

    r_1.getHurt(Damage(amount=3, damage_type="physical", source=None))

    r_1.draw()

    r_1.getHurt(Damage(amount=3, damage_type="physical", source=None))

    r_1.draw()

    #r_1.getHurt(Damage(amount=3, damage_type="physical", source=b_2))
    log.saveLog()  

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()