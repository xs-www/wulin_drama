import random
from entity import Entity, Character, Damage
from grid import GameGrid, GameBoard
from character import BattleCharacter
from util import *
from typing import Optional

def attack(attacker_info: tuple, defender_info: tuple, skill = None) -> int:
    attacker, attacker_team = attacker_info
    defender, defender_team = defender_info

    damage: Damage = attacker.getAttackDamage()
    log.console(f"[{attacker_team}]{attacker.getAttr('name')}({attacker.getInGameAttr('atk')}/{attacker.getInGameAttr('current_hp')})[/{attacker_team}] 攻击 [{defender_team}]{defender.getAttr('name')}({defender.getInGameAttr('atk')}/{defender.getInGameAttr('current_hp')})[/{defender_team}] 造成了 {damage.amount} 点伤害。")
    defender.getHurt(damage)
    log.console(f"[{defender_team}]{defender.getAttr('name')} 当前状态： {defender.getInGameAttr('atk')}/{defender.getInGameAttr('current_hp')}[/{defender_team}]")

    counter_attack_damage: Damage = defender.getAttackDamage()
    log.console(f"[{defender_team}]{defender.getAttr('name')}({defender.getInGameAttr('atk')}/{defender.getInGameAttr('current_hp')})[/{defender_team}] 反击了 [{attacker_team}]{attacker.getAttr('name')}({attacker.getInGameAttr('atk')}/{attacker.getInGameAttr('current_hp')})[/{attacker_team}] 造成了 {counter_attack_damage.amount} 点伤害。")
    attacker.getHurt(counter_attack_damage)
    log.console(f"[{attacker_team}]{attacker.getAttr('name')} 当前状态： {attacker.getInGameAttr('atk')}/{attacker.getInGameAttr('current_hp')}[/{attacker_team}]")


def attackSelector(char: Character, aimed_group: GameGrid) -> Entity | None:

    hate_values = aimed_group.getHateValue()
    hate_matrix = char.getAttr("hate_bias_matrix")

    weighted_hate = matrixMultiply(hate_matrix, hate_values)

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


def attackSimulator(game_board: GameBoard, save_state: bool = False, battle_id: Optional[str] = None):
    """
    战斗模拟器
    :param game_board: 游戏棋盘
    :param save_state: 是否保存战斗状态
    :param battle_id: 战斗ID（用于保存）
    """
    red_group = game_board.red_group
    blue_group = game_board.blue_group

    round_counter = 1
    battle_history = []  # 记录战斗历史

    import time

    # 记录初始状态
    if save_state:
        initial_state = captureBattleState(game_board, round_counter, "start")
        battle_history.append(initial_state)

    while not game_board.isBattleOver():
        time.sleep(0.5)
        log.console(f"--- Round {round_counter} ---")
        
        act_list = generateActionList(game_board)
        for char_info in act_list:
            attacker : Character = char_info[0]
            if not attacker.alive:
                continue
            aimed_group = game_board.getOtherTeam(attacker)
            aimed_entity = attackSelector(attacker, aimed_group)
            if aimed_entity is not None and isinstance(aimed_entity, Character):
                attack((attacker, game_board.getTeamById(attacker.getAttr("team_id")).lower()), (aimed_entity, game_board.getTeamById(aimed_entity.getAttr("team_id")).lower()))
                if not aimed_entity.isAlive():
                    log.console(f"{aimed_entity.getAttr('name')} has been defeated!")
        
        # 记录回合结束状态
        if save_state:
            round_state = captureBattleState(game_board, round_counter, "end")
            battle_history.append(round_state)
        
        round_counter += 1

    log.console("Battle Over!")
    
    # 保存战斗状态
    if save_state:
        saveBattleHistory(battle_id or "default", battle_history)
    
    return battle_history if save_state else None

def generateActionList(game_board: GameBoard) -> list[Character]:

    red_group = game_board.red_group
    blue_group = game_board.blue_group
    character_list : list[Character] = red_group.getAliveCharacterList() + blue_group.getAliveCharacterList()
    info_list = [(char, char.getInGameAttr("speed") + roll(10), game_board.getTeamById(char.getAttr("team_id")) ) for char in character_list]
    info_list.sort(key=lambda x: x[1], reverse=True)

    return info_list

# @todo
class RoundManager:

    def __init__(self):
        self.current_round = 1

    def nextRound(self):
        self.current_round += 1


def captureBattleState(game_board: GameBoard, round_num: int, phase: str) -> dict:
    """
    捕获当前战斗状态
    :param game_board: 游戏棋盘
    :param round_num: 回合数
    :param phase: 阶段 (start/end)
    :return: 状态字典
    """
    def serializeCharacter(char: Character) -> dict:
        """序列化角色信息"""
        return {
            "id": char.getAttr("team_id") + "_" + char.getAttr("name"),
            "name": char.getAttr("name"),
            "position": char.getAttr("position"),
            "team_id": char.getAttr("team_id"),
            "atk": char.getInGameAttr("atk"),
            "current_hp": char.getInGameAttr("current_hp"),
            "max_hp": char.getInGameAttr("max_hp"),
            "speed": char.getInGameAttr("speed"),
            "alive": char.isAlive()
        }
    
    red_chars = [serializeCharacter(c) for c in game_board.red_group.getCharacterList()]
    blue_chars = [serializeCharacter(c) for c in game_board.blue_group.getCharacterList()]
    
    return {
        "round": round_num,
        "phase": phase,
        "timestamp": timestampTime(),
        "red_team": red_chars,
        "blue_team": blue_chars,
        "battle_over": game_board.isBattleOver()
    }


def saveBattleHistory(battle_id: str, history: list):
    """
    保存战斗历史
    :param battle_id: 战斗ID
    :param history: 战斗历史列表
    """
    try:
        from content_manager import BattleStateManager
        manager = BattleStateManager()
        
        battle_data = {
            "battle_id": battle_id,
            "rounds": len(history),
            "history": history
        }
        
        filepath = manager.save_battle_state(battle_id, battle_data)
        log.console(f"战斗状态已保存到: {filepath}", "OK")
    except Exception as e:
        log.console(f"保存战斗状态失败: {e}", "ERROR")
