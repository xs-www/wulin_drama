import random
from entity import Entity
from grid import GameGrid, GameBoard
from character import BattleCharacter
from util import *

def attack(attacker: BattleCharacter, defender: BattleCharacter, skill = None, log : Log = None) -> int:
    damage = attacker.getAttackPower()
    defender.getHurt(damage)
    log.consle(f"{attacker.name} attacks {defender.name} for {damage} damage. {defender.name} HP left: {defender.current_health}")
    conter_attack_damage = max(1, defender.getAttackPower() // 2)
    attacker.getHurt(conter_attack_damage)
    log.consle(f"{defender.name} counterattacks {attacker.name} for {conter_attack_damage} damage. {attacker.name} HP left: {attacker.current_health}")
    

def attackSelector(character: BattleCharacter, aimed_group: GameGrid) -> Entity | None:

    hate_values = aimed_group.getHateValue()
    hate_matrix = character.hate_matrix

    weighted_hate = matrix_multiply(hate_matrix, hate_values)

    def find_max_hate_idx(weighted_hate: list) -> int:
        max_value = -1
        max_index_i = -1
        max_index_j = -1
        for i in range(len(weighted_hate)):
            for j in range(len(weighted_hate[i])):
                if weighted_hate[i][j] > max_value:
                    max_value = weighted_hate[i][j]
                    max_index_i = i
                    max_index_j = j
        return (max_index_i, max_index_j)
    
    max_i, max_j = find_max_hate_idx(weighted_hate)
    aimed_position = (["front", "middle", "back"][max_i], max_j + 1)
    aimed_entity = aimed_group.getCharacterByPosition(aimed_position)

    return aimed_entity


def attackSimulator(game_board: GameBoard) -> Log:

    red_group = game_board.red_group
    blue_group = game_board.blue_group

    log = Log()
    round_counter = 1

    import time

    while not game_board.isBattleOver():
        time.sleep(0.5)
        log.consle(f"--- Round {round_counter} ---")
        round_counter += 1
        act_list = generateActionList(game_board)
        for char_info in act_list:
            attacker : BattleCharacter = char_info[0]
            if not attacker.alive:
                continue
            aimed_group = blue_group if attacker.getTeamId() == red_group.team_id else red_group
            aimed_entity = attackSelector(attacker, aimed_group)
            if aimed_entity is not None and isinstance(aimed_entity, BattleCharacter):
                attack(attacker, aimed_entity, log=log)
                if not aimed_entity.isAlive():
                    log.consle(f"{aimed_entity.name} has been defeated!")

    log.consle("Battle Over!")
    return log

def generateActionList(game_board: GameBoard) -> list[BattleCharacter]:

    red_group = game_board.red_group
    blue_group = game_board.blue_group
    character_list : list[BattleCharacter] = red_group.getAliveCharacterList() + blue_group.getAliveCharacterList()
    info_list = [(char, char.getSpeed() + roll(10), char.getTeamId()) for char in character_list]
    info_list.sort(key=lambda x: x[1], reverse=True)

    return info_list