BEGIN TRANSACTION;
CREATE TABLE character (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                localization TEXT,
                attack_power INTEGER DEFAULT 4,
                health_points INTEGER DEFAULT 8,
                speed INTEGER DEFAULT 2,
                hate_value INTEGER DEFAULT 1,
                price INTEGER DEFAULT 1,
                weapon TEXT,
                energy INTEGER DEFAULT 0,
                avaliable_location TEXT,
                fetter TEXT,
                hate_matrix TEXT
            , "max_initiative" TEXT);
INSERT INTO "character" VALUES('0001','wooden_man','木头人',1,1000,5,1,1,'fist',3,'["front", "back"]',NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0002','1up','一前',1,21,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0003','1down','一后',3,7,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0004','2up','二前',1,28,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0005','2down','二后',3,10,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0006','3up','三前',2,28,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0007','3down','三后',4,13,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0008','4up','四前',2,43,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0009','4down','四后',4,19,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0010','5up','五前',3,43,5,1,4,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
INSERT INTO "character" VALUES('0011','5down','五后',5,25,5,1,4,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]','10');
CREATE TABLE event (
                id TEXT PRIMARY KEY,
                name TEXT,
                context TEXT
            );
INSERT INTO "event" VALUES('onAttack','攻击时','{"signature": "onAttack(source: Character, target: Character)", "description": "攻击时", "subevents": ["beforeAttack -> 攻击前", "afterAttack -> 攻击后"]}');
INSERT INTO "event" VALUES('onTurnStart','回合开始时','{"signature": "onTurnStart(trun_count: int)", "description": "回合开始时", "subevents": []}');
INSERT INTO "event" VALUES('onGameStart','对局开始时','{"signature": "onGameStart()", "description": "对局开始时", "subevents": []}');
INSERT INTO "event" VALUES('onAct','行动时','{"signature": "onAct(entity: Character, action_type: Enum(ActionType))", "description": "行动时", "subevents": []}');
INSERT INTO "event" VALUES('onGetHurt','受伤时','{"signature": "onGetHurt(entity: Character, damage: Damage)", "description": "受伤时", "subevents": ["beforeGetHurt -> 受伤前", "afterGetHurt -> 受伤后"]}');
INSERT INTO "event" VALUES('onEntityDead','实体死亡时','{"signature": "onEntityDead(entity: Character)", "description": "实体死亡时", "subevents": []}');
INSERT INTO "event" VALUES('onAttrChanged','属性变动时','{"signature": "onAttrChanged(entity: Character, attr: str, residual: int)", "description": "属性变动时", "subevents": []}');
INSERT INTO "event" VALUES('onSkillReleased','技能释放时','{"signature": "onSkillReleased(entity: Character, skill: Skill)", "description": "技能释放时", "subevents": []}');
INSERT INTO "event" VALUES('onBuffApplied','buff施加时','{"signature": "onBuffApplied(source: Character, target: Character, buff: Buff)", "description": "buff施加时", "subevents": []}');
INSERT INTO "event" VALUES('onBuffExpired','buff失效时','{"signature": "onBuffExpired(buff: Buff)", "description": "buff失效时", "subevents": []}');
INSERT INTO "event" VALUES('onBuffRemoved','buff移除时','{"signature": "onBuffRemoved(entity: Character, buff: Buff)", "description": "buff移除时", "subevents": []}');
INSERT INTO "event" VALUES('onAddStatu','施加状态时','{"signature": "onAddStatu(entity: Character, statu_id: str)", "description": "施加状态时", "subevents": []}');
INSERT INTO "event" VALUES('onRemoveStatu','状态移除时','{"signature": "onRemoveStatu(entity: Character, statu_id: str)", "description": "状态移除时", "subevents": []}');
INSERT INTO "event" VALUES('onHealthBelow:x','当血量低于10%','{"entity": "character"}');
CREATE TABLE keyword (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                type TEXT,
                trigger TEXT,
                condition TEXT,
                effects TEXT
            );
COMMIT;
