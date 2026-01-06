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
            );
INSERT INTO "character" VALUES('0001','wooden_man','木头人',1,1000,5,1,1,'fist',3,'["front", "back"]',NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0002','1up','一前',1,21,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0003','1down','一后',3,7,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0004','2up','二前',1,28,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0005','2down','二后',3,10,5,1,2,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0006','3up','三前',2,28,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0007','3down','三后',4,13,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0008','4up','四前',2,43,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0009','4down','四后',4,19,5,1,3,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0010','5up','五前',3,43,5,1,4,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
INSERT INTO "character" VALUES('0011','5down','五后',5,25,5,1,4,NULL,0,NULL,NULL,'[[1, 1, 1], [1, 1, 1], [1, 1, 1]]');
COMMIT;
