#from character import Character
from grid import GameGrid, GameBoard
import pygame, sys
from simulator import * 
from util import log, em
from entity import Damage, Character
from effect import Condition, Effect, Buff, BuffList
from keywords import *


from windows.main_menu import MainMenu

def main():

    pygame.init()

    e1 = Effect(
        "modify_attr", "HP+10%r", "self"
    )

    e2 = Effect(
        "modify_attr", "DMG+20%r", "damage"
    )

    e3 = Effect(
        "modify_attr", "ATK+10", "self"
    )

    bf1 = Buff("test", [e1, e3], 5, 1, -1)

    ch1 = Character.byId(1)

    ch1.draw()

    ch1.getHurt(Damage(damage=120, damage_type="physical", source=None))
    
    ch1.applyBuff(bf1)

    ch1.draw()


    

    #r_1.getHurt(Damage(amount=3, damage_type="physical", source=b_2))
    #log.saveLog()  

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()