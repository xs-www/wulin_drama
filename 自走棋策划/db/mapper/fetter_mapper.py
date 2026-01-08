"""
SQL strings for `fetter` table.
Columns:
- id (英文名)
- people_count (人数)  — 与 id 组成复合主键
- info (text)
"""

CREATE_FETTER_TABLE = '''
CREATE TABLE IF NOT EXISTS fetter (
    id TEXT NOT NULL,
    people_count INTEGER NOT NULL,
    info TEXT,
    PRIMARY KEY (id, people_count)
);
'''

# Basic CRUD templates
SELECT_FETTER_BY_ID_AND_COUNT = 'SELECT * FROM fetter WHERE id = ? AND people_count = ?'
INSERT_FETTER = 'INSERT INTO fetter (id, people_count, info) VALUES (?, ?, ?)'
UPDATE_FETTER = 'UPDATE fetter SET info = ? WHERE id = ? AND people_count = ?'
DELETE_FETTER = 'DELETE FROM fetter WHERE id = ? AND people_count = ?'
