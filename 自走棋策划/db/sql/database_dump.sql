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
INSERT INTO "character" VALUES('0002','Ch1',NULL,1,20,1,2,1,NULL,0,NULL,NULL,NULL);
INSERT INTO "character" VALUES('0003','Ch2',NULL,2,12,1,3,1,NULL,0,NULL,NULL,NULL);
INSERT INTO "character" VALUES('0004','Ch3',NULL,10,4,4,3,1,NULL,0,NULL,NULL,NULL);
INSERT INTO "character" VALUES('0005','Ch4',NULL,5,8,2,2,1,NULL,0,NULL,NULL,NULL);
INSERT INTO "character" VALUES('0006','Sisi','思思',5,10,3,1,2,NULL,4,NULL,NULL,NULL);
INSERT INTO "character" VALUES('0007','wuxie','张无邪',10,100,5,5,4,NULL,4,NULL,NULL,NULL);
COMMIT;
