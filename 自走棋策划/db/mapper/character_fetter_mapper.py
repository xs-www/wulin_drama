"""
SQL strings for `character_fetter` association table.
Associates characters with fetters. References composite key (fetter.id, fetter.people_count).
"""

CREATE_CHARACTER_FETTER_TABLE = '''
CREATE TABLE IF NOT EXISTS character_fetter (
    character_id TEXT NOT NULL,
    fetter_id TEXT NOT NULL,
    people_count INTEGER NOT NULL,
    PRIMARY KEY (character_id, fetter_id, people_count),
    FOREIGN KEY (character_id) REFERENCES character(id),
    FOREIGN KEY (fetter_id, people_count) REFERENCES fetter(id, people_count)
);
'''

# Basic CRUD templates
SELECT_FETTERS_BY_CHARACTER = 'SELECT * FROM character_fetter WHERE character_id = ?'
INSERT_CHARACTER_FETTER = 'INSERT INTO character_fetter (character_id, fetter_id, people_count) VALUES (?, ?, ?)'
DELETE_CHARACTER_FETTER = 'DELETE FROM character_fetter WHERE character_id = ? AND fetter_id = ? AND people_count = ?'
