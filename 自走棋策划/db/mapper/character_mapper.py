"""
SQL strings and helpers for `character` table.

Refactor note: `fetter` column removed — 羁绊已迁移到独立表 `fetter` 和关联表 `character_fetter`。

This module exposes:
- `CREATE_CHARACTER_TABLE` : DDL for creating the `character` table.
- `CHARACTER_COLUMNS` : ordered list of canonical columns for the table.
- helper functions `build_insert(data)` and `build_update(data, key='id')` that
  generate SQL and parameter lists dynamically from a mapping (类似 Java PO -> 自动 SQL)。
"""

CREATE_CHARACTER_TABLE = '''
CREATE TABLE IF NOT EXISTS character (
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
	hate_matrix TEXT,
	"max_initiative" TEXT
);
'''

# Ordered canonical columns for `character` table. 用于生成动态 SQL。
CHARACTER_COLUMNS = [
	'id',
	'name',
	'localization',
	'attack_power',
	'health_points',
	'speed',
	'hate_value',
	'price',
	'weapon',
	'energy',
	'avaliable_location',
	'hate_matrix',
	'max_initiative'
]

# 常用静态 SQL
SELECT_CHARACTER_BY_ID = 'SELECT * FROM character WHERE id = ?'
DELETE_CHARACTER = 'DELETE FROM character WHERE id = ?'

def _quote_col(col: str) -> str:
	# Only quote if contains special characters or reserved words; keep simple here
	if col == 'max_initiative':
		return '"max_initiative"'
	return col

def build_insert(data: dict) -> tuple:
	"""根据传入的 `data` 映射生成 INSERT 语句与参数列表。

	返回 (sql:str, params: list)。只会包含 `CHARACTER_COLUMNS` 中存在且在 `data` 中的列。
	"""
	cols = [c for c in CHARACTER_COLUMNS if c in data]
	if not cols:
		raise ValueError('No valid columns provided for insert')
	cols_sql = ', '.join(_quote_col(c) for c in cols)
	placeholders = ', '.join(['?'] * len(cols))
	sql = f'INSERT INTO character ({cols_sql}) VALUES ({placeholders})'
	params = [data[c] for c in cols]
	return sql, params


def build_update(data: dict, key: str = 'id') -> tuple:
	"""根据传入的 `data` 生成 UPDATE 语句与参数列表。

	`key` 指定 WHERE 子句使用的主键字段（默认 `id`），该字段必须存在于 `data` 中。
	返回 (sql:str, params:list)。
	"""
	if key not in data:
		raise ValueError(f'Primary key "{key}" missing in data for update')
	cols = [c for c in CHARACTER_COLUMNS if c in data and c != key]
	if not cols:
		raise ValueError('No updatable columns provided')
	set_sql = ', '.join(f'{_quote_col(c)} = ?' for c in cols)
	sql = f'UPDATE character SET {set_sql} WHERE {_quote_col(key)} = ?'
	params = [data[c] for c in cols] + [data[key]]
	return sql, params


def build_insert_or_replace(data: dict) -> tuple:
	"""辅助函数：生成 `INSERT OR REPLACE`（SQLite）语句，用于简便的 upsert 场景。
	返回 (sql, params)。"""
	cols = [c for c in CHARACTER_COLUMNS if c in data]
	if not cols:
		raise ValueError('No valid columns provided for insert_or_replace')
	cols_sql = ', '.join(_quote_col(c) for c in cols)
	placeholders = ', '.join(['?'] * len(cols))
	sql = f'INSERT OR REPLACE INTO character ({cols_sql}) VALUES ({placeholders})'
	params = [data[c] for c in cols]
	return sql, params

