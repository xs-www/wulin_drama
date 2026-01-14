from util import *
from entity import Character, Entity
from grid import GameRow, GameGrid, GameBoard
import uuid

class ShopEntity:

    def __init__(self):
        pass

class ShopRow(GameRow):

    def __init__(self, max_length=6):
        super().__init__(max_length=max_length)
        self.locked = [False] * self.max_length
        
    def isLocked(self, idx):
        idx -= 1  # Convert to 0-based index
        if 0 <= idx < self.max_length:
            return self.locked[idx]
        else:
            return False
        
    def refresh(self):
        for i in range(self.max_length):
            if not self.locked[i]:
                if self.getCharacterByPosition(i + 1) is not None:
                    self.removeCharacterByPosition(i + 1)
                self.setCharacter(Character.randomCharacter(), i + 1)

    def lock(self, idx):
        self.locked[idx-1] = True
    
    def unlock(self, idx):
        self.locked[idx-1] = False

    def draw(self):
        super().draw()
        for i in range(self.max_length):
            lock_status = "🔒" if self.isLocked(i + 1) else " "
            print(lock_status.rjust(7) if i == 0 else lock_status.rjust(12), end="")
        print()

class Shop:

    def __init__(self, owner=None):
        self.characters = ShopRow(6)
        self.grade = 0
        self.owner = owner
        self.characters.refresh()

    def buy(self, idx):
        char = self.characters.getCharacterByPosition(idx)
        if isinstance(char, Character):
            if self.owner.getAttr("money") >= char.getAttr("info.price"):
                self.owner.setAttr("money", self.owner.getAttr("money") - char.getAttr("info.price"))
                self.characters.removeCharacterByPosition(idx)
                log.console(f"玩家 {self.owner.getAttr('id')} 购买了角色 {char.getAttr('id')}，花费 {char.getAttr('info.price')} 金币。", "INFO")
                em.broadcast("shop.bought", player=self.owner, character=char)
                self.draw()
                return True
            else:
                log.console(f"玩家 {self.owner.getAttr('id')} 购买角色失败，金币不足。需要 {char.getAttr('info.price')}，但只有 {self.owner.getAttr('money')}。", "WARNING")
                return False
        else:
            log.console(f"玩家 {self.owner.getAttr('id')} 购买角色失败，索引 {idx} 处没有角色。", "WARNING")
            return False

    def refresh(self):
        if self.owner.getAttr("money") >= 2:
            self.owner.setAttr("money", self.owner.getAttr("money") - 2)
            self.characters.refresh()
            log.console(f"玩家 {self.owner.getAttr('id')} 刷新了商店，花费 2 金币。", "INFO")
            em.broadcast("shop.refreshed", player=self.owner)
        else:
            log.console(f"玩家 {self.owner.getAttr('id')} 刷新商店失败，金币不足。需要 2 金币，但只有 {self.owner.getAttr('money')}。", "WARNING")
            return
        self.draw()

    def upgrade(self):
        if self.owner.getAttr("money") >= 10:
            self.owner.setAttr("money", self.owner.getAttr("money") - 10)
            self.grade += 1
            log.console(f"玩家 {self.owner.getAttr('id')} 升级了商店到等级 {self.grade}，花费 10 金币。", "INFO")
            em.broadcast("shop.upgraded", player=self.owner, new_grade=self.grade)
            return True
        else:
            log.console(f"玩家 {self.owner.getAttr('id')} 升级商店失败，金币不足。需要 10 金币，但只有 {self.owner.getAttr('money')}。", "WARNING")
            return False

    def lock(self, idx):
        self.characters.lock(idx)
        pass

    def unlock(self, idx):
        self.characters.unlock(idx)
        pass

    def lockAll(self):
        for i in range(1, self.characters.max_length + 1):
            self.lock(i)
        pass

    def unlockAll(self):
        for i in range(1, self.characters.max_length + 1):
            self.unlock(i)
        pass

    def draw(self):
        print(f"|:  商店等级: {self.grade}  :|".center(60, " "))
        self.characters.draw()

class Player(Entity):

    def __init__(self, player_id=None):
        super().__init__()
        self.addAttr("id", player_id if player_id is not None else uuid.uuid4())
        self.addAttr("money", 0)
        self.addAttr("max.hp", 100)
        self.addAttr("current.hp", 100)

        self.characters = GameRow(max_length=10)
        self.shop = Shop(owner=self)
        self.team = GameGrid()

        self.setAttr("money", 5)
        em.register('shop.bought', self.onBuyCharacter)
        pass

    def setAttr(self, key: str, value):
        before_value = super().getAttr(key)
        if before_value != value:
            super().setAttr(key, value)
            em.broadcast('onAttrChange', player=self, attr=key, before=before_value, after=value)

    def onBuyCharacter(self, player: "Player", character: Character):
        if player == self:
            self.characters.setCharacter(character)
        self.characters.draw()

class MainGame:

    def __init__(self):
        self.player = Player()
        self.game_stage = (1, 1)  # (stage, round)

    def update(self):
        pass
        
    def start(self):
        while True:
            self.draw()
            print("按下任意按键进入休整阶段，输入0退出游戏.")
            ipt = input("选择命令: ").lower()
            if ipt == "0":
                break
            self._developTeam()

    def _developTeam(self):
        self.draw()
        while True:
            if not self.waitingForInput():
                break
    
    def _buyCharacter(self):
        print("金币：", self.player.getAttr("money"))
        self.player.shop.draw()
        while True:
            print("输入0退出购买.")
            idx = input("输入要购买的角色索引 (1-6): ")
            if idx == "0":
                return False
            if not idx.isdigit() or not (1 <= int(idx) <= 6):
                print("无效的索引.")
                continue
            if self.player.shop.buy(int(idx)):
                break
        return True
    
    def _setCharacter(self):
        self.player.characters.draw()
        if self.player.characters.isEmpty():
            print("没有可用的角色.")
            return False
        while True:
            idx = input("选择要放置的角色 (1-10): ")
            if idx.isdigit() and (1 <= int(idx) <= 10):
                char = self.player.characters.getCharacterByPosition(int(idx))
                if not isinstance(char, Character):
                    print("该位置没有角色.")
                    continue
                break
            else:
                print("无效的索引.")
        self.player.team.draw()
        while True:
            row = input("选择要放置的行 (front/middle/back/bench): ").lower()
            if row not in ["front", "middle", "back", "bench"]:
                print("无效的行.")
                continue
            aim_idx = input("选择要放置的位置 (1-3): ")
            if not aim_idx.isdigit() or not (1 <= int(aim_idx) <= 3):
                print("无效的位置.")
                continue
            self.player.team.setCharacter(char, row, int(aim_idx))
            self.player.characters.removeCharacterByPosition(int(idx))
            break
        self.draw()
        return True

    def _lockShop(self):
        self.player.shop.draw()
        while True:
            idx = input("输入要‘all’或者锁定的角色索引 (1-6), 输入0退出: ")
            if idx.lower() == "all":
                self.player.shop.lockAll()
                self.player.shop.draw()
                break
            if idx == "0":
                return True
            if not idx.isdigit() or not (1 <= int(idx) <= 6):
                print("无效的索引.")
                continue
            self.player.shop.lock(int(idx))
            self.player.shop.draw()
            break
        self.player.shop.draw()
        return True

    def waitingForInput(self):
        print("可选命令（输入序号） \n1. 购买角色\n2. 刷新商店\n3. 升级商店\n4. 锁定商店\n5. 设置角色\n9. 显示信息\n0. 准备战斗！")
        ipt = input("选择命令: ").lower()
        match ipt:
            case "1" | "buy character":
                self._buyCharacter()
                return True
            case "2" | "refresh shop":
                self.player.shop.refresh()
                return True
            case "3" | "upgrade shop":
                self.player.shop.upgrade()
                return True
            case "4" | "lock shop":
                self._lockShop()
                return True
            case "5" | "set character":
                self._setCharacter()
                return True
            case "9" | "draw":
                self.draw()
                return True
            case "0" | "exit":
                print("前往战斗.")
                return False
            case _:
                print("未知命令.")
                return True
    
    def draw(self):
        print("\n--- Player Info ---")
        print(f"Money: {self.player.getAttr('money')}")
        print("\n--- Shop ---")
        self.player.shop.draw()
        print("\n--- Team ---")
        self.player.team.draw()
        print("\n--- Characters ---")
        self.player.characters.draw()
        print("\n-------------------\n")

if __name__ == "__main__":
    game = MainGame()
    game.start()