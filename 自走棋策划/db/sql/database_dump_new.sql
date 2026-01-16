BEGIN TRANSACTION;
DROP TABLE IF EXISTS `Character`;
CREATE TABLE Character (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, attack_power INTEGER DEFAULT 4, health_points INTEGER DEFAULT 8, speed INTEGER DEFAULT 2, hate_value INTEGER DEFAULT 1, price INTEGER DEFAULT 1, weapon TEXT, energy INTEGER DEFAULT 0, avaliable_location TEXT, hate_matrix TEXT
        , max_initiative INTEGER DEFAULT 10);
INSERT INTO "Character" VALUES(1,'测试角色1',4,8,2,1,2,NULL,0,NULL,NULL,10);
INSERT INTO "Character" VALUES(2,'测试角色2',4,8,2,1,3,'[]',0,'[]','[]',10);
INSERT INTO "Character" VALUES(4,'惊鸿',4,8,2,1,1,'''[]''',0,'''[]''','''[[1,1,1],[1,1,1],[1,1,1]]''',10);
DROP TABLE IF EXISTS `CharacterFetter`;
CREATE TABLE CharacterFetter (
        character_id INTEGER NOT NULL, fetter_id TEXT NOT NULL
        , PRIMARY KEY (character_id, fetter_id)
        );
INSERT INTO "CharacterFetter" VALUES(1,'武当');
INSERT INTO "CharacterFetter" VALUES(2,'武当');
INSERT INTO "CharacterFetter" VALUES(2,'峨眉');
INSERT INTO "CharacterFetter" VALUES(4,'武道院');
DROP TABLE IF EXISTS `Fetter`;
CREATE TABLE Fetter (
        id TEXT NOT NULL, numofpeople INTEGER NOT NULL, description TEXT
        , PRIMARY KEY (id, numofpeople)
        );
INSERT INTO "Fetter" VALUES('武当',3,'反击时附带30%攻击伤害');
INSERT INTO "Fetter" VALUES('峨眉',3,'连击1次，触发攻击特效');
INSERT INTO "Fetter" VALUES('炁体源流',3,'最大能量增加3');
INSERT INTO "Fetter" VALUES('天山',2,'');
INSERT INTO "Fetter" VALUES('天山',6,'');
INSERT INTO "Fetter" VALUES('华山',3,'反击时附带30%攻击伤害');
INSERT INTO "Fetter" VALUES('华山',6,'真气攻击额外攻击2个目标，造成50%伤害');
INSERT INTO "Fetter" VALUES('华山',9,'反击时附带90%攻击伤害');
INSERT INTO "Fetter" VALUES('武当',6,'反击时附带60%攻击伤害');
INSERT INTO "Fetter" VALUES('武当',9,'反击时附带90%攻击伤害');
INSERT INTO "Fetter" VALUES('峨眉',5,'连击2次，触发攻击特效');
INSERT INTO "Fetter" VALUES('峨眉',7,'连击3次，触发攻击特效');
INSERT INTO "Fetter" VALUES('少林',2,'回合结束时，回复真气与血量');
INSERT INTO "Fetter" VALUES('少林',4,'回合结束时，回复真气与血量');
INSERT INTO "Fetter" VALUES('潇湘',3,'穿临时武器，并依据穿着获得属性加成');
INSERT INTO "Fetter" VALUES('潇湘',5,'穿临时武器，并依据穿着获得属性加成');
INSERT INTO "Fetter" VALUES('潇湘',7,'穿临时武器，并依据穿着获得属性加成');
INSERT INTO "Fetter" VALUES('九流门',2,'');
INSERT INTO "Fetter" VALUES('蓬莱派',2,'每次攻击后进入招架状态');
INSERT INTO "Fetter" VALUES('南朝',3,'手牌流，将手牌中的英雄养大');
INSERT INTO "Fetter" VALUES('定北军',3,'亡语，使一个友方角色继承一部分自己的力量');
INSERT INTO "Fetter" VALUES('北朝',3,'颁布政令，派系角色获得全局无论在哪里的加成');
INSERT INTO "Fetter" VALUES('武道院',3,'开局时确定一个属性，每回合获得该属性的加成，最多五次');
INSERT INTO "Fetter" VALUES('东瀛',1,'只上一张牌时获得加成');
INSERT INTO "Fetter" VALUES('远程攻击',2,'123');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('Character',4);
COMMIT;
