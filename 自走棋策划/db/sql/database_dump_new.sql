BEGIN TRANSACTION;
DROP TABLE IF EXISTS `Character`;
CREATE TABLE Character (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, attack_power INTEGER DEFAULT 4, health_points INTEGER DEFAULT 8, speed INTEGER DEFAULT 2, hate_value INTEGER DEFAULT 1, price INTEGER DEFAULT 1, weapon TEXT, energy INTEGER DEFAULT 0, avaliable_location TEXT, hate_matrix TEXT
        , max_initiative INTEGER DEFAULT 10);
INSERT INTO "Character" VALUES(1,'测试角色1',4,8,2,1,2,NULL,0,NULL,NULL,10);
INSERT INTO "Character" VALUES(2,'测试角色2',4,8,2,1,3,'[]',0,'[]','[]',10);
DROP TABLE IF EXISTS `CharacterFetter`;
CREATE TABLE CharacterFetter (
        character_id INTEGER NOT NULL, fetter_id TEXT NOT NULL
        , PRIMARY KEY (character_id, fetter_id)
        );
INSERT INTO "CharacterFetter" VALUES(1,'武当');
INSERT INTO "CharacterFetter" VALUES(2,'武当');
INSERT INTO "CharacterFetter" VALUES(2,'峨眉');
DROP TABLE IF EXISTS `Fetter`;
CREATE TABLE Fetter (
        id TEXT NOT NULL, numofpeople INTEGER NOT NULL, description TEXT
        , PRIMARY KEY (id, numofpeople)
        );
INSERT INTO "Fetter" VALUES('武当',3,'略');
INSERT INTO "Fetter" VALUES('武当',5,'略');
INSERT INTO "Fetter" VALUES('少林',3,'略');
INSERT INTO "Fetter" VALUES('峨眉',3,'略');
INSERT INTO "Fetter" VALUES('炁体源流',3,'最大能量增加3');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('Character',3);
COMMIT;
