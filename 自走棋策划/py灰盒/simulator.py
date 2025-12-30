import random
from entity import Entity
from grid import GameGrid, GameBoard
from character import BattleCharacter
from util import *

def attack(attacker_info: tuple, defender_info: tuple, skill = None) -> int:
    attacker, attacker_team = attacker_info
    defender, defender_team = defender_info

    damage = attacker.getAttackPower()
    log.console(f"[{attacker_team}]{attacker.name}({attacker.attack_power}/{attacker.current_health})[/{attacker_team}] 攻击 [{defender_team}]{defender.name}({defender.attack_power}/{defender.current_health})[/{defender_team}] 造成了 {damage} 点伤害。")
    defender.getHurt(damage)
    log.console(f"[{defender_team}]{defender.name} 当前状态： {defender.attack_power}/{defender.current_health}[/{defender_team}]")

    counter_attack_damage = max(1, defender.getAttackPower() // 2)
    log.console(f"[{defender_team}]{defender.name}({defender.attack_power}/{defender.current_health})[/{defender_team}] 反击了 [{attacker_team}]{attacker.name}({attacker.attack_power}/{attacker.current_health})[/{attacker_team}] 造成了 {counter_attack_damage} 点伤害。")
    attacker.getHurt(counter_attack_damage)
    log.console(f"[{attacker_team}]{attacker.name} 当前状态： {attacker.attack_power}/{attacker.current_health}[/{attacker_team}]")


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


def attackSimulator(game_board: GameBoard):
    red_group = game_board.red_group
    blue_group = game_board.blue_group

    round_counter = 1

    import time

    while not game_board.isBattleOver():
        time.sleep(0.5)
        log.console(f"--- Round {round_counter} ---")
        round_counter += 1
        act_list = generateActionList(game_board)
        for char_info in act_list:
            attacker : BattleCharacter = char_info[0]
            if not attacker.alive:
                continue
            aimed_group = blue_group if attacker.getTeamId() == red_group.team_id else red_group
            aimed_entity = attackSelector(attacker, aimed_group)
            if aimed_entity is not None and isinstance(aimed_entity, BattleCharacter):
                attack((attacker, game_board.getTeamById(attacker.getTeamId()).lower()), (aimed_entity, game_board.getTeamById(aimed_entity.getTeamId()).lower()))
                if not aimed_entity.isAlive():
                    log.console(f"{aimed_entity.name} has been defeated!")

    log.console("Battle Over!")

def generateActionList(game_board: GameBoard) -> list[BattleCharacter]:

    red_group = game_board.red_group
    blue_group = game_board.blue_group
    character_list : list[BattleCharacter] = red_group.getAliveCharacterList() + blue_group.getAliveCharacterList()
    info_list = [(char, char.getSpeed() + roll(10), game_board.getTeamById(char.getTeamId())) for char in character_list]
    info_list.sort(key=lambda x: x[1], reverse=True)

    return info_list