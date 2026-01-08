from util import *
import uuid

def keywordFactory(keyword_name: str):
    keyword_classes = {
        "Sheild": Sheild,
    }
    return keyword_classes.get(keyword_name, None)


sheild = {
    "id": "sheild",
    "name": "护盾",
    "description": "抵消一次受到的伤害",
    "type": "pessive",
    "trigger": "onGetHurt",
    "condition": [
        {
            "type": "has_statu",
            "param": "sheild"
        }
    ],
    "effects": [
        {
            "type": "modify_attr",
            "param": "DMG=0",
            "mode": "damage"
        },
        {
            "type": "remove_statu",
            "param": "sheild",
            "mode": "self"
        }
    ]
}



class Sheild:

    uuid_dict = {}

    def __init__(self, owner = None):
        self.id = uuid.uuid4()
        self.owner = owner
        self.amount = 1  # 护盾数量，表示可以抵消多少次伤害
        em.on("onGetHurt")(self._handle)
    
    def _handle(self, **context):
        if self.owner == context['target']:
            damage = context['damage']
            if damage.amount > 0:
                log.console(f"{self.owner.getAttr('name')} 的护盾抵消了所有伤害！", "SHIELD")
                damage.amount = 0
                self.amount -= 1
                if not self.isAlive():
                    self.owner.removeKeyword(self)
                    em.unregister("onGetHurt", self._handle)
                    log.console(f"{self.owner.getAttr('name')} 的护盾消失了！", "SHIELD")
    
    def isAlive(self):
        return self.amount > 0