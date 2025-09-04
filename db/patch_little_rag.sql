-- Brand canonical & aliasing
CREATE TABLE IF NOT EXISTS brands(
  brand_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE,
  site TEXT,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS brand_aliases(
  brand_id INTEGER,
  alias TEXT,
  UNIQUE(brand_id, alias)
);

-- Little RAG cache
CREATE TABLE IF NOT EXISTS little_rag_cache(
  id INTEGER PRIMARY KEY,
  event_date TEXT,
  brand TEXT,
  group_title TEXT,
  group_id TEXT,
  last_active_ts TEXT,
  match_conf REAL,
  status TEXT,
  ttl_expiry_ts TEXT
);

-- Group health
CREATE TABLE IF NOT EXISTS group_health(
  group_id TEXT PRIMARY KEY,
  last_active_ts TEXT,
  inactivity_days INTEGER,
  calendar_ok INTEGER
);
